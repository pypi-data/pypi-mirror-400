import datetime
import json
import re
import sys
import threading
import types

from nsj_rest_lib.settings import get_logger

from nsj_rest_lib2.compiler.edl_model.primitives import REGEX_EXTERNAL_REF
from nsj_rest_lib2.compiler.model import RelationDependency
from nsj_rest_lib2.compiler.util.type_naming_util import compile_namespace_keys
from nsj_rest_lib2.exception import MissingEntityConfigException
from nsj_rest_lib2.redis_config import get_redis
from nsj_rest_lib2.settings import ESCOPO_RESTLIB2, MIN_TIME_SOURCE_REFRESH


class LoadedEntity:
    def __init__(self):
        self.dto_class_name: str = ""
        self.entity_class_name: str = ""
        self.entity_hash: str = ""
        self.loaded_at: datetime.datetime = datetime.datetime.now()
        self.api_expose: bool = False
        self.api_verbs: list[str] = []
        self.relations_dependencies: list[RelationDependency] = []
        self.service_account: str | None = None
        self.insert_function_class_name: str | None = None
        self.update_function_class_name: str | None = None
        self.insert_function_name: str | None = None
        self.update_function_name: str | None = None
        self.get_function_name: str | None = None
        self.list_function_name: str | None = None
        self.delete_function_name: str | None = None
        self.get_function_type_class_name: str | None = None
        self.list_function_type_class_name: str | None = None
        self.delete_function_type_class_name: str | None = None
        self.retrieve_after_insert: bool = False
        self.retrieve_after_update: bool = False
        self.retrieve_after_partial_update: bool = False
        self.post_response_dto_class_name: str | None = None
        self.put_response_dto_class_name: str | None = None
        self.patch_response_dto_class_name: str | None = None
        self.custom_json_post_response: bool = False
        self.custom_json_put_response: bool = False
        self.custom_json_patch_response: bool = False
        self.custom_json_get_response: bool = False
        self.custom_json_list_response: bool = False
        self.custom_json_delete_response: bool = False


class Namespace:
    def __init__(self):
        self.key: str = ""
        self.loaded_entities: dict[str, LoadedEntity] = {}
        self.entities_dict: dict = {}
        self.module: types.ModuleType = types.ModuleType("empty")


namespaces_dict: dict[str, Namespace] = {}


class EntityLoader:
    def __init__(self) -> types.NoneType:
        self._lock = threading.Lock()

    def load_entity_source(
        self,
        entity_resource: str,
        tenant: str | None,
        grupo_empresarial: str | None,
        escopo: str = ESCOPO_RESTLIB2,
        force_reload: bool = False,
    ) -> tuple[
        str,
        str,
        dict,
        bool,
        list[str],
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        bool,
        bool,
        bool,
        str | None,
        str | None,
        str | None,
        bool,
        bool,
        bool,
        bool,
        bool,
        bool,
    ]:
        # Assumind o escopo default se necessário
        if not escopo:
            escopo = ESCOPO_RESTLIB2

        # Montando as chaves dos namespaces
        grupo_key, tenant_key, default_key = compile_namespace_keys(
            tenant, grupo_empresarial
        )

        result = self._search_entity_namespace_in_memory(
            entity_resource, grupo_key, tenant_key, default_key
        )

        # Se conseguiu localizar na memória, verifica se houve alteração no hash, em relação ao redis
        if result is not None:
            # Desempacotando o result e recuperando informações do namespace
            (
                entity_config_key,
                namespace,
            ) = result

            loaded_entity = namespace.loaded_entities[entity_resource]
            dto_class_name = loaded_entity.dto_class_name
            entity_class_name = loaded_entity.entity_class_name
            entities_dict = namespace.entities_dict
            api_expose = loaded_entity.api_expose
            api_verbs = loaded_entity.api_verbs
            service_account = loaded_entity.service_account
            relations_dependencies = loaded_entity.relations_dependencies
            insert_function_class_name = loaded_entity.insert_function_class_name
            update_function_class_name = loaded_entity.update_function_class_name
            insert_function_name = loaded_entity.insert_function_name
            update_function_name = loaded_entity.update_function_name
            get_function_name = loaded_entity.get_function_name
            list_function_name = loaded_entity.list_function_name
            delete_function_name = loaded_entity.delete_function_name
            get_function_type_class_name = (
                loaded_entity.get_function_type_class_name
            )
            list_function_type_class_name = (
                loaded_entity.list_function_type_class_name
            )
            delete_function_type_class_name = (
                loaded_entity.delete_function_type_class_name
            )

            # Verificando se alguma de suas dependências precisariam ser recarregadas
            for rd in relations_dependencies:
                if rd.entity_resource is None or rd.entity_scope is None:
                    raise RuntimeError(
                        f"Erro: Dependência de entidade mal formada na entidade {entity_resource}."
                    )

                self.load_entity_source(
                    rd.entity_resource,
                    str(rd.tenant),
                    str(rd.grupo_empresarial),
                    rd.entity_scope,
                    force_reload=force_reload,
                )

            # Se o tempo entre o carregamento e agora for maior do que MIN_TIME_SOURCE_REFRESH minutos,
            # verifica se precisa de refresh
            time_diff = datetime.datetime.now() - loaded_entity.loaded_at

            if (
                time_diff.total_seconds() >= MIN_TIME_SOURCE_REFRESH * 60
                or force_reload
            ):
                # Renovando o tempo de refresh
                loaded_entity.loaded_at = datetime.datetime.now()

                # Recuperando do Redis direto pela key (faz uma só chamada ao redis)
                loaded_config = self._load_entity_config_from_redis(
                    entity_resource,
                    grupo_key,
                    tenant_key,
                    default_key,
                    entity_config_key,
                    escopo=escopo,
                )

                # Se não achar no redis, usa o que estava em memória
                if not loaded_config:
                    return (
                        dto_class_name,
                        entity_class_name,
                        entities_dict,
                        api_expose,
                        api_verbs,
                        service_account,
                        insert_function_class_name,
                        update_function_class_name,
                        insert_function_name,
                        update_function_name,
                        get_function_name,
                        list_function_name,
                        delete_function_name,
                        get_function_type_class_name,
                        list_function_type_class_name,
                        delete_function_type_class_name,
                        loaded_entity.retrieve_after_insert,
                        loaded_entity.retrieve_after_update,
                        loaded_entity.retrieve_after_partial_update,
                        loaded_entity.post_response_dto_class_name,
                        loaded_entity.put_response_dto_class_name,
                        loaded_entity.patch_response_dto_class_name,
                        loaded_entity.custom_json_post_response,
                        loaded_entity.custom_json_put_response,
                        loaded_entity.custom_json_patch_response,
                        loaded_entity.custom_json_get_response,
                        loaded_entity.custom_json_list_response,
                        loaded_entity.custom_json_delete_response,
                    )

                # Desempacotando resultado
                entity_config_key, entity_config_str = loaded_config

                # Executando o código da entidade, só se houver mudança no hash
                result_execute = self._execute_entity_source(
                    entity_config_str,
                    entity_config_key,
                    entity_resource,
                    check_refresh=True,
                )

                # Se não carregou novo código, usa o que estava em memória
                if result_execute is None:
                    return (
                        dto_class_name,
                        entity_class_name,
                        entities_dict,
                        api_expose,
                        api_verbs,
                        service_account,
                        insert_function_class_name,
                        update_function_class_name,
                        insert_function_name,
                        update_function_name,
                        get_function_name,
                        list_function_name,
                        delete_function_name,
                        get_function_type_class_name,
                        list_function_type_class_name,
                        delete_function_type_class_name,
                        loaded_entity.retrieve_after_insert,
                        loaded_entity.retrieve_after_update,
                        loaded_entity.retrieve_after_partial_update,
                        loaded_entity.post_response_dto_class_name,
                        loaded_entity.put_response_dto_class_name,
                        loaded_entity.patch_response_dto_class_name,
                        loaded_entity.custom_json_post_response,
                        loaded_entity.custom_json_put_response,
                        loaded_entity.custom_json_patch_response,
                        loaded_entity.custom_json_get_response,
                        loaded_entity.custom_json_list_response,
                        loaded_entity.custom_json_delete_response,
                    )
                else:
                    (
                        dto_class_name,
                        entity_class_name,
                        namespace,
                        api_expose,
                        api_verbs,
                        service_account,
                        insert_function_class_name,
                        update_function_class_name,
                        insert_function_name,
                        update_function_name,
                        get_function_name,
                        list_function_name,
                        delete_function_name,
                        get_function_type_class_name,
                        list_function_type_class_name,
                        delete_function_type_class_name,
                        retrieve_after_insert,
                        retrieve_after_update,
                        retrieve_after_partial_update,
                        post_response_dto_class_name,
                        put_response_dto_class_name,
                        patch_response_dto_class_name,
                        custom_json_post_response,
                        custom_json_put_response,
                        custom_json_patch_response,
                        custom_json_get_response,
                        custom_json_list_response,
                        custom_json_delete_response,
                    ) = result_execute
                    return (
                        dto_class_name,
                        entity_class_name,
                        namespace.entities_dict,
                        api_expose,
                        api_verbs,
                        service_account,
                        insert_function_class_name,
                        update_function_class_name,
                        insert_function_name,
                        update_function_name,
                        get_function_name,
                        list_function_name,
                        delete_function_name,
                        get_function_type_class_name,
                        list_function_type_class_name,
                        delete_function_type_class_name,
                        retrieve_after_insert,
                        retrieve_after_update,
                        retrieve_after_partial_update,
                        post_response_dto_class_name,
                        put_response_dto_class_name,
                        patch_response_dto_class_name,
                        custom_json_post_response,
                        custom_json_put_response,
                        custom_json_patch_response,
                        custom_json_get_response,
                        custom_json_list_response,
                        custom_json_delete_response,
                    )
            else:
                # Se não deu o intervalo de verificação do refresh, retorna o que está em memória
                return (
                    dto_class_name,
                    entity_class_name,
                    entities_dict,
                    api_expose,
                    api_verbs,
                    service_account,
                    insert_function_class_name,
                    update_function_class_name,
                    insert_function_name,
                    update_function_name,
                    get_function_name,
                    list_function_name,
                    delete_function_name,
                    get_function_type_class_name,
                    list_function_type_class_name,
                    delete_function_type_class_name,
                    loaded_entity.retrieve_after_insert,
                    loaded_entity.retrieve_after_update,
                    loaded_entity.retrieve_after_partial_update,
                    loaded_entity.post_response_dto_class_name,
                    loaded_entity.put_response_dto_class_name,
                    loaded_entity.patch_response_dto_class_name,
                    loaded_entity.custom_json_post_response,
                    loaded_entity.custom_json_put_response,
                    loaded_entity.custom_json_patch_response,
                    loaded_entity.custom_json_get_response,
                    loaded_entity.custom_json_list_response,
                    loaded_entity.custom_json_delete_response,
                )

        # Se não conseguir recuperar a entidade, procura no redis:
        loaded_config = self._load_entity_config_from_redis(
            entity_resource,
            grupo_key,
            tenant_key,
            default_key,
            None,
            escopo=escopo,
        )

        # Se também não achar no redis, lanca exceção
        if not loaded_config:
            raise MissingEntityConfigException()

        # Desempacotando resultado
        entity_config_key, entity_config_str = loaded_config

        # Executando o código da entidade
        result_execute = self._execute_entity_source(
            entity_config_str, entity_config_key, entity_resource
        )

        if result_execute is None:
            raise RuntimeError(
                f"Erro desconhecido carregando entidade: {entity_resource}"
            )
        (
            dto_class_name,
            entity_class_name,
            namespace,
            api_expose,
            api_verbs,
            service_account,
            insert_function_class_name,
            update_function_class_name,
            insert_function_name,
            update_function_name,
            get_function_name,
            list_function_name,
            delete_function_name,
            get_function_type_class_name,
            list_function_type_class_name,
            delete_function_type_class_name,
            retrieve_after_insert,
            retrieve_after_update,
            retrieve_after_partial_update,
            post_response_dto_class_name,
            put_response_dto_class_name,
            patch_response_dto_class_name,
            custom_json_post_response,
            custom_json_put_response,
            custom_json_patch_response,
            custom_json_get_response,
            custom_json_list_response,
            custom_json_delete_response,
        ) = result_execute

        return (
            dto_class_name,
            entity_class_name,
            namespace.entities_dict,
            api_expose,
            api_verbs,
            service_account,
            insert_function_class_name,
            update_function_class_name,
            insert_function_name,
            update_function_name,
            get_function_name,
            list_function_name,
            delete_function_name,
            get_function_type_class_name,
            list_function_type_class_name,
            delete_function_type_class_name,
            retrieve_after_insert,
            retrieve_after_update,
            retrieve_after_partial_update,
            post_response_dto_class_name,
            put_response_dto_class_name,
            patch_response_dto_class_name,
            custom_json_post_response,
            custom_json_put_response,
            custom_json_patch_response,
            custom_json_get_response,
            custom_json_list_response,
            custom_json_delete_response,
        )

    def clear_namespaces(self):
        """
        Clears all loaded namespaces from memory.

        This method removes all entries from the namespaces_dict, effectively resetting
        the in-memory cache of loaded entities and their associated namespaces.
        """
        with self._lock:
            namespaces_dict.clear()

    def _ensure_dynamic_package(self):
        """
        Garante que exista um pacote 'dynamic' em sys.modules.
        """
        pkg = sys.modules.get("dynamic")
        if pkg is None:
            pkg = types.ModuleType("dynamic")
            pkg.__path__ = []  # marca como pacote
            pkg.__package__ = "dynamic"
            sys.modules["dynamic"] = pkg
        return pkg

    def _execute_entity_source(
        self,
        entity_config_str: str,
        entity_config_key: str,
        entity_resource: str,
        check_refresh: bool = False,
    ) -> tuple[
        str,
        str,
        Namespace,
        bool,
        list[str],
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        str | None,
        bool,
        bool,
        bool,
        str | None,
        str | None,
        str | None,
        bool,
        bool,
        bool,
        bool,
        bool,
        bool,
    ] | None:
        # Interpretando o json de configuração da entidade
        try:
            entity_config = json.loads(entity_config_str)

            dto_class_name = entity_config["dto_class_name"]
            entity_class_name = entity_config["entity_class_name"]
            source_dto = entity_config["source_dto"]
            source_entity = entity_config["source_entity"]
            entity_hash = entity_config["entity_hash"]

            api_expose = entity_config["api_expose"]
            # api_resource = entity_config["api_resource"]
            api_verbs = entity_config["api_verbs"]
            service_account = entity_config.get("service_account")
            insert_function_class_name = entity_config.get(
                "insert_function_class_name"
            )
            insert_function_name = entity_config.get("insert_function_name")
            insert_function_code = entity_config.get("source_insert_function")
            update_function_class_name = entity_config.get(
                "update_function_class_name"
            )
            update_function_name = entity_config.get("update_function_name")
            update_function_code = entity_config.get("source_update_function")
            get_function_name = entity_config.get("get_function_name")
            list_function_name = entity_config.get("list_function_name")
            delete_function_name = entity_config.get("delete_function_name")
            get_function_type_class_name = entity_config.get(
                "get_function_type_class_name"
            )
            list_function_type_class_name = entity_config.get(
                "list_function_type_class_name"
            )
            delete_function_type_class_name = entity_config.get(
                "delete_function_type_class_name"
            )
            retrieve_after_insert = entity_config.get(
                "retrieve_after_insert", False
            )
            retrieve_after_update = entity_config.get(
                "retrieve_after_update", False
            )
            retrieve_after_partial_update = entity_config.get(
                "retrieve_after_partial_update", False
            )
            post_response_dto_class_name = entity_config.get(
                "post_response_dto_class_name"
            )
            put_response_dto_class_name = entity_config.get(
                "put_response_dto_class_name"
            )
            patch_response_dto_class_name = entity_config.get(
                "patch_response_dto_class_name"
            )
            custom_json_post_response = entity_config.get(
                "custom_json_post_response", False
            )
            custom_json_put_response = entity_config.get(
                "custom_json_put_response", False
            )
            custom_json_patch_response = entity_config.get(
                "custom_json_patch_response", False
            )
            custom_json_get_response = entity_config.get(
                "custom_json_get_response", False
            )
            custom_json_list_response = entity_config.get(
                "custom_json_list_response", False
            )
            custom_json_delete_response = entity_config.get(
                "custom_json_delete_response", False
            )
            get_function_code = entity_config.get("source_get_function_type")
            list_function_code = entity_config.get("source_list_function_type")
            delete_function_code = entity_config.get("source_delete_function_type")
            relations_dependencies = [
                RelationDependency().from_dict(rd)
                for rd in entity_config.get("relations_dependencies", [])
            ]
        except json.JSONDecodeError as e:
            if not check_refresh:
                raise RuntimeError(
                    f"Erro ao decodificar JSON da entidade {entity_resource}; na chave {entity_config_key}: {e}"
                )
            else:
                get_logger().error(
                    f"Erro ao decodificar JSON da entidade {entity_resource}; na chave {entity_config_key}: {e}"
                )
                return None

        # Verificando se alguma de suas dependências precisariam ser carregadas (ou recarregadas)
        for rd in relations_dependencies:
            if rd.entity_resource is None or rd.entity_scope is None:
                raise RuntimeError(
                    f"Erro: Dependência de entidade mal formada na entidade {entity_resource}."
                )

            self.load_entity_source(
                rd.entity_resource,
                str(rd.tenant),
                str(rd.grupo_empresarial),
                rd.entity_scope,
            )

        # Verificando se a entidade precisa ou não de refresh
        if check_refresh:
            loaded_namespace = namespaces_dict.get(entity_config_key)
            if not loaded_namespace:
                return None

            loaded_entity = loaded_namespace.loaded_entities.get(entity_resource)
            if not loaded_entity:
                return None

            if loaded_entity.entity_hash == entity_hash:
                return None

        # Imprimindo alerta de load no log
        get_logger().debug(
            f"Carregando entidade {entity_resource} no namespace {entity_config_key}."
        )

        # Carregando a entidade no namespace
        with self._lock:
            self._ensure_dynamic_package()

            namespace = namespaces_dict.get(entity_config_key)
            if namespace is None:
                namespace = Namespace()
                namespace.key = entity_config_key
                namespaces_dict[entity_config_key] = namespace

            # Hot reload: removendo o módulo do sys.modules, se existir
            full_name = f"dynamic.{entity_config_key}"
            # if full_name in sys.modules:
            #     sys.modules.pop(full_name)

            # Executando o código da entidade
            module = sys.modules.get(full_name)
            if not module:
                module = types.ModuleType(full_name)
                module.__package__ = "dynamic"
                module.__dict__["__builtins__"] = __builtins__
                sys.modules[full_name] = module

                parent = sys.modules["dynamic"]
                setattr(parent, entity_config_key, module)

                namespace.module = module
                namespace.entities_dict = module.__dict__

            get_logger().debug(
                f"Executando o código da entidade {entity_resource} no namespace {entity_config_key}. Código:"
            )
            get_logger().debug(f"Entity source:\n{source_entity}")
            get_logger().debug(f"DTO source:\n{source_dto}")

            if insert_function_code:
                self._safe_exec(
                    insert_function_code,
                    namespace.entities_dict,
                    "Insert Function source",
                )

            if update_function_code:
                self._safe_exec(
                    update_function_code,
                    namespace.entities_dict,
                    "Update Function source",
                )

            if get_function_code:
                self._safe_exec(
                    get_function_code,
                    namespace.entities_dict,
                    "Get FunctionType source",
                )

            if list_function_code:
                self._safe_exec(
                    list_function_code,
                    namespace.entities_dict,
                    "List FunctionType source",
                )

            if delete_function_code:
                self._safe_exec(
                    delete_function_code,
                    namespace.entities_dict,
                    "Delete FunctionType source",
                )

            self._safe_exec(source_entity, namespace.entities_dict, "Entity source")
            self._safe_exec(source_dto, namespace.entities_dict, "DTO source")

            # Gravando a entidade no dict de entidades carregadas
            loaded_entity = LoadedEntity()
            loaded_entity.dto_class_name = dto_class_name
            loaded_entity.entity_class_name = entity_class_name
            loaded_entity.entity_hash = entity_hash
            loaded_entity.api_expose = api_expose
            loaded_entity.api_verbs = api_verbs
            loaded_entity.service_account = service_account
            loaded_entity.relations_dependencies = relations_dependencies
            loaded_entity.insert_function_class_name = insert_function_class_name
            loaded_entity.update_function_class_name = update_function_class_name
            loaded_entity.insert_function_name = insert_function_name
            loaded_entity.update_function_name = update_function_name
            loaded_entity.get_function_name = get_function_name
            loaded_entity.list_function_name = list_function_name
            loaded_entity.delete_function_name = delete_function_name
            loaded_entity.get_function_type_class_name = (
                get_function_type_class_name
            )
            loaded_entity.list_function_type_class_name = (
                list_function_type_class_name
            )
            loaded_entity.delete_function_type_class_name = (
                delete_function_type_class_name
            )
            loaded_entity.retrieve_after_insert = bool(retrieve_after_insert)
            loaded_entity.retrieve_after_update = bool(retrieve_after_update)
            loaded_entity.retrieve_after_partial_update = bool(
                retrieve_after_partial_update
            )
            loaded_entity.post_response_dto_class_name = (
                post_response_dto_class_name
            )
            loaded_entity.put_response_dto_class_name = (
                put_response_dto_class_name
            )
            loaded_entity.patch_response_dto_class_name = (
                patch_response_dto_class_name
            )
            loaded_entity.custom_json_post_response = bool(
                custom_json_post_response
            )
            loaded_entity.custom_json_put_response = bool(
                custom_json_put_response
            )
            loaded_entity.custom_json_patch_response = bool(
                custom_json_patch_response
            )
            loaded_entity.custom_json_get_response = bool(
                custom_json_get_response
            )
            loaded_entity.custom_json_list_response = bool(
                custom_json_list_response
            )
            loaded_entity.custom_json_delete_response = bool(
                custom_json_delete_response
            )

            namespace.loaded_entities[entity_resource] = loaded_entity

        return (
            dto_class_name,
            entity_class_name,
            namespace,
            api_expose,
            api_verbs,
            service_account,
            insert_function_class_name,
            update_function_class_name,
            insert_function_name,
            update_function_name,
            get_function_name,
            list_function_name,
            delete_function_name,
            get_function_type_class_name,
            list_function_type_class_name,
            delete_function_type_class_name,
            bool(retrieve_after_insert),
            bool(retrieve_after_update),
            bool(retrieve_after_partial_update),
            post_response_dto_class_name,
            put_response_dto_class_name,
            patch_response_dto_class_name,
            bool(custom_json_post_response),
            bool(custom_json_put_response),
            bool(custom_json_patch_response),
            bool(custom_json_get_response),
            bool(custom_json_list_response),
            bool(custom_json_delete_response),
        )

    def _safe_exec(self, source_code, context, description):
        try:
            exec(source_code, context)
        except Exception as e:
            get_logger().error(f"Error executing {description}: {e}")
            raise

    def _load_entity_config_from_redis(
        self,
        entity_resource: str,
        grupo_key: str,
        tenant_key: str,
        default_key: str,
        entity_config_key: str | None,
        escopo: str,
    ) -> tuple[str, str] | None:
        get_logger().debug(
            f"Procurando a configuração da entidade {entity_resource} no redis. Tenant key: {tenant_key} e Grupo key: {grupo_key}"
        )

        if entity_config_key is not None:
            entity_config_str = get_redis(
                "entity_config", escopo, entity_config_key, entity_resource
            )

        else:
            entity_config_key = grupo_key
            entity_config_str = get_redis(
                "entity_config", escopo, grupo_key, entity_resource
            )
            if entity_config_str is None:
                entity_config_key = tenant_key
                entity_config_str = get_redis(
                    "entity_config", escopo, tenant_key, entity_resource
                )
            if entity_config_str is None:
                entity_config_key = default_key
                entity_config_str = get_redis(
                    "entity_config", escopo, default_key, entity_resource
                )

        # Se não encontrar no redis, retorna None
        if entity_config_str is None:
            return None

        return (entity_config_key, entity_config_str)

    def _search_entity_namespace_in_memory(
        self,
        entity_resource: str,
        grupo_key: str,
        tenant_key: str,
        default_key: str,
    ) -> tuple[str, Namespace] | None:
        namespace = None
        entity_config_key = None

        # Pesquisando a entidade no namespace mais específico (grupo_empresarial)
        grupo_namespace = namespaces_dict.get(grupo_key)
        if grupo_namespace and entity_resource in grupo_namespace.loaded_entities:
            entity_config_key = grupo_key
            namespace = grupo_namespace

        # Pesquisando a entidade no namespace intermediário (tenant)
        tenant_namespace = namespaces_dict.get(tenant_key)
        if tenant_namespace and entity_resource in tenant_namespace.loaded_entities:
            entity_config_key = tenant_key
            namespace = tenant_namespace

        # Pesquisando a entidade no namespace padrão (default)
        default_namespace = namespaces_dict.get(default_key)
        if default_namespace and entity_resource in default_namespace.loaded_entities:
            entity_config_key = default_key
            namespace = default_namespace

        if namespace and entity_config_key:
            return (entity_config_key, namespace)
        else:
            return None
