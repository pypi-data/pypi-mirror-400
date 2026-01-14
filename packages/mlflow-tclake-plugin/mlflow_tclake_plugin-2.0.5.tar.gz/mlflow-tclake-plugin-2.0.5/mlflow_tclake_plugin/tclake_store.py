import base64
import json
import os
import time
import uuid
from datetime import datetime

from cachetools import TTLCache
from tencentcloud.common import credential
from tencentcloud.common.common_client import CommonClient
from tencentcloud.common.profile.client_profile import ClientProfile

from mlflow.entities.model_registry import RegisteredModel, ModelVersion, ModelVersionTag
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE, RESOURCE_ALREADY_EXISTS
from mlflow.store.model_registry import SEARCH_REGISTERED_MODEL_MAX_RESULTS_THRESHOLD, \
    SEARCH_MODEL_VERSION_MAX_RESULTS_THRESHOLD
from mlflow.store.model_registry.abstract_store import AbstractStore
from mlflow.utils.annotations import experimental
from mlflow.utils.search_utils import SearchModelUtils, SearchModelVersionUtils
from mlflow.store.entities.paged_list import PagedList
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


def to_string(obj):
    if obj is None:
        return "None"
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return json.dumps(obj, indent=2)
    try:
        return json.dumps(obj, indent=2)
    except:
        return str(obj)


tencent_cloud_debug = os.getenv("TENCENTCLOUD_DEBUG", None)


def log_msg(msg):
    if tencent_cloud_debug:
        print(msg)


def _get_create_time_from_audit(audit):
    dt_str = audit["CreatedTime"]
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp() * 1000)


def _get_last_updated_time_from_audit(audit):
    dt_str = audit["LastModifiedTime"]
    if dt_str is None or len(dt_str) == 0:
        return _get_create_time_from_audit(audit)
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp() * 1000)


def _get_description(resp):
    if resp is None or "Comment" not in resp:
        return None
    return resp["Comment"]


TCLAKE_MLFLOW_TAG_PREFIX = "tclake.tag."
TCLAKE_MLFLOW_RUN_ID_KEY = "tclake.mlflow.run_id"
TCLAKE_MLFLOW_RUN_LINK_KEY = "tclake.mlflow.run_link"
TCLAKE_UUID_KEY = "tccatalog.identifier"
TCLAKE_MLFLOW_MODEL_SIGNATURE_KEY = "tclake.mlflow.model_signature"
TCLAKE_WEDATA_PROJECT_ID_KEY = "wedata.project"
TCLAKE_MLFLOW_MODEL_ARTIFACT_PATH_KEY = "tclake.mlflow.artifact_path"


def _set_kv_to_properties(key, value, properties=None):
    if properties is None:
        properties = []
    if value is not None:
        properties.append({"Key": key, "Value": value})
    return properties


def _get_kv_from_properties(properties, key):
    if properties is None:
        return None
    for p in properties:
        if p["Key"] == key:
            return p["Value"]
    return None


def _get_uuid_from_properties(properties):
    return _get_kv_from_properties(properties, TCLAKE_UUID_KEY)


def _set_run_id_to_properties(run_id, properties=None):
    return _set_kv_to_properties(TCLAKE_MLFLOW_RUN_ID_KEY, run_id, properties)


def _get_run_id_from_properties(properties):
    return _get_kv_from_properties(properties, TCLAKE_MLFLOW_RUN_ID_KEY)


def _set_run_link_to_properties(run_link, properties):
    return _set_kv_to_properties(TCLAKE_MLFLOW_RUN_LINK_KEY, run_link, properties)


def _get_run_link_from_properties(properties):
    return _get_kv_from_properties(properties, TCLAKE_MLFLOW_RUN_LINK_KEY)


def _add_tag_to_properties(tag, properties=None):
    if tag and tag.value is not None:
        properties = _set_kv_to_properties(tag.key, tag.value, properties)
        properties += _set_kv_to_properties(TCLAKE_MLFLOW_TAG_PREFIX + tag.key, tag.value, properties)
    return properties

def _add_tags_to_properties(tags, properties=None):
    if tags:
        for tag in tags:
            properties = _add_tag_to_properties(tag, properties)
    return properties

def _add_project_id_to_properties(project_id, properties=None):
    if project_id is not None:
        properties = _set_kv_to_properties(TCLAKE_WEDATA_PROJECT_ID_KEY, project_id, properties)
    return properties



def parse_model_signatures_from_dict(signature_dict):
    signatures = []
    inputs_str = signature_dict.get("inputs")
    if inputs_str:
        inputs = json.loads(inputs_str)
        for input_item in inputs:
            model_signature = {
                "name": input_item.get("name", ""), 
                "type": "INPUT",
                "inputFlag": "true"
            }
            type_val = input_item.get("type")
            if type_val is not None:
                if type_val == "tensor":
                    tensor_spec = input_item.get("tensor-spec", {}).get("dtype", "")
                    if tensor_spec:
                        model_signature["type"] = str(tensor_spec)
                else:
                    model_signature["type"] = str(type_val)
            
            signatures.append(model_signature)

    outputs_str = signature_dict.get("outputs")
    if outputs_str:
        outputs = json.loads(outputs_str)
        for output_item in outputs:    
            name_val = output_item.get("name", "")
            if not name_val:
                name_val = output_item.get("prediction_column_name", "")
            model_signature = {
                "name": name_val, 
                "type": "OUTPUT", 
                "inputFlag": "false"
            }
            type_val = output_item.get("type")
            if type_val is not None:
                if type_val == "tensor":
                    tensor_spec = output_item.get("tensor-spec", {}).get("dtype", "")
                    if tensor_spec:
                        model_signature["type"] = str(tensor_spec)
                else:
                    model_signature["type"] = str(type_val)
            
            signatures.append(model_signature)
    
    log_msg(f"parse model version signatures: {signatures}")
    return signatures      


def _add_model_signature_to_properties(source, properties):
    log_msg("model source is {}".format(source))
    try:
        from mlflow.models.model import get_model_info
        model_info = get_model_info(source)
        signature = model_info.signature
        log_msg("model {} signature is {}".format(source, signature))
        if signature:
            sig_json = json.dumps(parse_model_signatures_from_dict(signature.to_dict()))
            log_msg("model {} signature json is {}".format(source, sig_json))
        else:
            log_msg(f"Registered model signature is not found in source artifact location '{source}'")
            sig_json = json.dumps([])
    except Exception as e:
        log_msg(f"Failed to get model signature from {source}: {e}")
        sig_json = json.dumps([])
    properties = _set_kv_to_properties(TCLAKE_MLFLOW_MODEL_SIGNATURE_KEY, sig_json, properties)
    return properties


def _add_model_artifact_path_to_properties(source, properties):
    log_msg("model source is {}".format(source))
    model_info = get_model_info(source)
    path = model_info.artifact_path
    log_msg("model {} artifact_path is {}".format(source, path))
    properties = _set_kv_to_properties(TCLAKE_MLFLOW_MODEL_ARTIFACT_PATH_KEY, path, properties)
    return properties


def _get_tags_from_properties(properties):
    if properties is None:
        return None
    tags = []
    for p in properties:
        if p["Key"].startswith(TCLAKE_MLFLOW_TAG_PREFIX):
            tags.append(ModelVersionTag(p["Key"][len(TCLAKE_MLFLOW_TAG_PREFIX):], p["Value"]))
    return tags


def _append_tag_key_prefix(key):
    return TCLAKE_MLFLOW_TAG_PREFIX + key


def _get_model_version(version):
    return str(version)


def _set_model_version(version):
    return int(version)


def _make_model(resp):
    properties = resp["Properties"]
    audit = resp["Audit"]
    return RegisteredModel(
        name=resp["Name"],
        creation_timestamp=_get_create_time_from_audit(audit),
        last_updated_timestamp=_get_last_updated_time_from_audit(audit),
        description=_get_description(resp),
        tags=_get_tags_from_properties(properties),
    )


def _get_model_version_name(entity):
    return "{}.{}.{}".format(entity["CatalogName"], entity["SchemaName"], entity["ModelName"])


def _make_model_version(entity, name):
    properties = entity["Properties"]
    audit = entity["Audit"]
    return ModelVersion(
        name=name,
        version=_get_model_version(entity["Version"]),
        creation_timestamp=_get_create_time_from_audit(audit),
        last_updated_timestamp=_get_last_updated_time_from_audit(audit),
        description=_get_description(entity),
        source=entity["Uri"],
        run_id=_get_run_id_from_properties(properties),
        tags=_get_tags_from_properties(properties),
        run_link=_get_run_link_from_properties(properties),
        status="READY",
    )


def get_tencent_cloud_headers():
    header_json = os.getenv("TENCENTCLOUD_HEADER_JSON", None)
    if header_json is None:
        return None
    return json.loads(header_json)


def get_tencent_cloud_client_profile():
    endpoint = os.getenv("TENCENTCLOUD_ENDPOINT", None)
    if endpoint is None:
        return None
    client_profile = ClientProfile()
    client_profile.httpProfile.endpoint = endpoint
    return client_profile


def _parse_page_token(page_token):
    decoded_token = base64.b64decode(page_token)
    parsed_token = json.loads(decoded_token)
    return parsed_token


def _create_page_token(offset, search_id):
    return base64.b64encode(json.dumps({"offset": offset, "search_id": search_id}).encode("utf-8"))


@experimental
class TCLakeStore(AbstractStore):
    """
    Client for an Open Source Unity Catalog Server accessed via REST API calls.
    """

    def __init__(self, store_uri=None, tracking_uri=None):
        super().__init__(store_uri, tracking_uri)
        log_msg("initializing tencent tclake client {} {}".format(store_uri, tracking_uri))
        sid = os.getenv("TENCENTCLOUD_SECRET_ID", "")
        if len(sid) == 0:
            raise MlflowException("TENCENTCLOUD_SECRET_ID is not set")
        sk = os.getenv("TENCENTCLOUD_SECRET_KEY", "")
        if len(sk) == 0:
            raise MlflowException("TENCENTCLOUD_SECRET_KEY is not set")
        token = os.getenv("TENCENTCLOUD_TOKEN", None)
        client_profile = get_tencent_cloud_client_profile()
        cred = credential.Credential(sid, sk, token)
        parts = store_uri.split(":")
        if len(parts) < 2:
            raise MlflowException("set store_uri tclake:{region}")
        region = parts[1]
        self.client = CommonClient("tccatalog", "2024-10-24", cred, region, client_profile)
        self.headers = get_tencent_cloud_headers()
        self.default_catalog_name = os.getenv("TENCENTCLOUD_DEFAULT_CATALOG_NAME", "default")
        self.default_schema_name = os.getenv("TENCENTCLOUD_DEFAULT_SCHEMA_NAME", "default")
        self.project_Id = os.getenv("WEDATA_PROJECT_ID", "")
        cache_size = int(os.getenv("TCLAKE_CACHE_SIZE", "100"))
        cache_ttl = int(os.getenv("TCLAKE_CACHE_TTL_SECS", "300"))
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        log_msg("initialized tencent tclake client successfully {} {} {} {} {}".format(
            region, client_profile, self.headers, cache_size, cache_ttl))

    def _split_model_name(self, name):
        parts = name.split(".")
        if len(parts) == 1:
            return [self.default_catalog_name, self.default_schema_name, parts[0]]
        if len(parts) == 2:
            return [self.default_catalog_name, parts[0], parts[1]]
        if len(parts) == 3:
            return parts
        raise MlflowException("invalid model name: {}, must be catalog.schema.model".format(name))

    def _call(self, action, req):
        log_msg("req: {}\n{}".format(action, json.dumps(req, indent=2)))
        body = self.client.call(action, req, headers=self.headers)
        body_obj = json.loads(body)
        log_msg("body: {}\n{}".format(action, json.dumps(body_obj, indent=2)))
        resp = body_obj["Response"]
        return resp

    def _get_model_version_numbers(self, name):
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
        }
        resp = self._call("DescribeModelVersionNumbers", req_body)
        return resp["Versions"]

    def _get_model_version_by_alias(self, name, alias):
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersions": self._get_model_version_numbers(name)
        }
        resp = self._call("DescribeModelVersions", req_body)
        model_version = None
        for mv in resp["ModelVersions"]:
            if alias in mv["Aliases"]:
                model_version = mv
                break
        if model_version is None:
            return None
        return _make_model_version(model_version, name)

    def create_registered_model(self, name, tags=None, description=None):
        log_msg("create_registered_model {} {} {}".format(name, tags, description))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        properties = []
        _add_tags_to_properties(tags, properties)
        _add_project_id_to_properties(self.project_Id, properties)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "Comment": description if description else "",
            "Properties": properties
        }

        try:
            resp = self._call("CreateModel", req_body)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                if e.code == "FailedOperation.MetalakeAlreadyExistsError":
                    raise MlflowException(
                        f"Registered Model (name={name}) already exists.",
                        RESOURCE_ALREADY_EXISTS,
                    )
            raise
        return _make_model(resp["Model"])


    def update_registered_model(self, name, description):
        log_msg("update_register_model {} {}".format(name, description))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "NewComment": description if description else ""
        }
        resp = self._call("ModifyModelComment", req_body)
        return _make_model(resp["Model"])

    def rename_registered_model(self, name, new_name):
        log_msg("rename_register_model {} {}".format(name, new_name))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "NewName": new_name
        }
        resp = self._call("ModifyModelName", req_body)
        return _make_model(resp["Model"])

    def delete_registered_model(self, name):
        log_msg("delete_register_model {}".format(name))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
        }
        resp = self._call("DropModel", req_body)
        if not resp["Dropped"]:
            raise MlflowException("Failed to delete model {}".format(name))

    def _fetch_all_models(self):
        req_body = {
            "Offset": 0,
            "Limit": 200,
            "SnapshotBased": True,
            "SnapshotId": ""
        }
        resp = self._call("SearchModels", req_body)
        total = resp['TotalCount']
        model_list = resp['Models']
        while len(model_list) < total:
            time.sleep(0.05)
            req_body["Offset"] += req_body["Limit"]
            req_body["SnapshotId"] = resp["SnapshotId"]
            resp = self._call("SearchModels", req_body)
            model_list.extend(resp['Models'])
            if len(resp['Models']) < req_body["Limit"]:
                break
        return [_make_model(model) for model in model_list]

    def search_registered_models(
            self, filter_string=None, max_results=None, order_by=None, page_token=None
    ):
        log_msg("search_registered_models {} {} {} {}".format(
            filter_string, max_results, order_by, page_token))
        if not isinstance(max_results, int) or max_results < 1:
            raise MlflowException(
                "Invalid value for max_results. It must be a positive integer,"
                f" but got {max_results}",
                INVALID_PARAMETER_VALUE,
            )

        if max_results > SEARCH_REGISTERED_MODEL_MAX_RESULTS_THRESHOLD:
            raise MlflowException(
                "Invalid value for request parameter max_results. It must be at most "
                f"{SEARCH_REGISTERED_MODEL_MAX_RESULTS_THRESHOLD}, but got value {max_results}",
                INVALID_PARAMETER_VALUE,
            )
        if page_token is None:
            registered_models = self._fetch_all_models()
            filtered_rms = SearchModelUtils.filter(registered_models, filter_string)
            sorted_rms = SearchModelUtils.sort(filtered_rms, order_by)
            if len(sorted_rms) == 0:
                return PagedList([], None)
            search_id = "model_" + str(uuid.uuid4())
            page_token = _create_page_token(0, search_id)
            self.cache[search_id] = sorted_rms
            log_msg("search_registered_models add cache {} {} {} {} {} {}".format(
                filter_string, max_results, order_by, page_token, search_id, len(sorted_rms)))
        return self._get_page_list(page_token, max_results)

    def get_registered_model(self, name):
        log_msg("get_registered_model {}".format(name))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
        }
        resp = self._call("DescribeModel", req)
        return _make_model(resp["Model"])

    def get_latest_versions(self, name, stages=None):
        log_msg("get_latest_versions {} {}".format(name, stages))
        if stages is not None:
            raise NotImplementedError("Method not support stages")
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
        }
        resp = self._call("DescribeModelVersions", req)
        return [
            _make_model_version(mv, name)
            for mv in resp["ModelVersions"]
        ]

    def set_registered_model_tag(self, name, tag):
        log_msg("set_registered_model_tag {} {}".format(name, tag))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "Properties": _add_tag_to_properties(tag)
        }
        self._call("ModifyModelProperties", req)

    def delete_registered_model_tag(self, name, key):
        log_msg("delete_registered_model_tag {} {}".format(name, key))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "RemovedKeys": [_append_tag_key_prefix(key)]
        }
        self._call("ModifyModelProperties", req)

    def create_model_version(
            self,
            name,
            source,
            run_id=None,
            tags=None,
            run_link=None,
            description=None,
            local_model_path=None,
    ):
        log_msg("create_model_version {} {} {} {} {} {} {}".format(
            name, source, run_id, tags, run_link, description, local_model_path))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        version_alias = str(uuid.uuid4())
        properties = []
        _add_tags_to_properties(tags, properties)
        _set_run_id_to_properties(run_id, properties)
        _set_run_link_to_properties(run_link, properties)
        _add_model_signature_to_properties(source, properties)
        _add_project_id_to_properties(self.project_Id, properties)
        _add_model_artifact_path_to_properties(source, properties)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "Uri": source,
            "Comment": description if description else "",
            "Properties": properties,
            "Aliases": [version_alias]
        }
        self._call("CreateModelVersion", req_body)
        return self._get_model_version_by_alias(name, version_alias)

    def update_model_version(self, name, version, description):
        log_msg("update_model_version {} {} {}".format(name, version, description))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersion": _set_model_version(version),
            "NewComment": description if description else ""
        }
        resp = self._call("ModifyModelVersionComment", req_body)
        return _make_model_version(resp["ModelVersion"], name)

    def transition_model_version_stage(self, name, version, stage, archive_existing_versions):
        raise NotImplementedError("Method not implemented")

    def delete_model_version(self, name, version):
        log_msg("delete_model_version {} {}".format(name, version))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersion": _set_model_version(version),
        }
        resp = self._call("DropModelVersion", req_body)
        if not resp["Dropped"]:
            raise Exception("Failed to delete model version {} {}".format(name, version))

    def get_model_version(self, name, version):
        log_msg("get_model_version {} {}".format(name, version))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req_body = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersion": _set_model_version(version),
        }
        resp = self._call("DescribeModelVersion", req_body)
        return _make_model_version(resp["ModelVersion"], name)

    def _fetch_all_model_versions(self):
        req_body = {
            "Offset": 0,
            "Limit": 200,
            "SnapshotBased": True,
            "SnapshotId": ""
        }
        resp = self._call("SearchModelVersions", req_body)
        total = resp['TotalCount']
        model_version_list = resp['ModelVersions']
        while len(model_version_list) < total:
            time.sleep(0.05)
            req_body["Offset"] += req_body["Limit"]
            req_body["SnapshotId"] = resp["SnapshotId"]
            resp = self._call("SearchModelVersions", req_body)
            model_version_list.extend(resp['ModelVersions'])
            if len(resp['ModelVersions']) < req_body["Limit"]:
                break
        return [_make_model_version(model_version, _get_model_version_name(model_version)) for model_version in
                model_version_list]

    def search_model_versions(
            self, filter_string=None, max_results=None, order_by=None, page_token=None
    ):
        log_msg("search_model_versions {} {} {} {}".format(
            filter_string, max_results, order_by, page_token))
        if not isinstance(max_results, int) or max_results < 1:
            raise MlflowException(
                "Invalid value for max_results. It must be a positive integer,"
                f" but got {max_results}",
                INVALID_PARAMETER_VALUE,
            )

        if max_results > SEARCH_MODEL_VERSION_MAX_RESULTS_THRESHOLD:
            raise MlflowException(
                "Invalid value for request parameter max_results. It must be at most "
                f"{SEARCH_MODEL_VERSION_MAX_RESULTS_THRESHOLD}, but got value {max_results}",
                INVALID_PARAMETER_VALUE,
            )
        if page_token is None:
            model_versions = self._fetch_all_model_versions()
            filtered_mvs = SearchModelVersionUtils.filter(model_versions, filter_string)
            sorted_mvs = SearchModelVersionUtils.sort(
                filtered_mvs,
                order_by or ["last_updated_timestamp DESC", "name ASC", "version_number DESC"],
            )
            if len(sorted_mvs) == 0:
                return PagedList([], None)
            search_id = "model_version_" + str(uuid.uuid4())
            page_token = _create_page_token(0, search_id)
            self.cache[search_id] = sorted_mvs
            log_msg("search_model_versions add cache {} {} {} {} {} {}".format(
                filter_string, max_results, order_by, page_token, search_id, len(sorted_mvs)))

        return self._get_page_list(page_token, max_results)

    def _get_page_list(self, page_token, max_results):
        token_info = _parse_page_token(page_token)
        log_msg("_get_page_list token_info {} {} {}".format(
            page_token, max_results, token_info))
        sorted_mvs = self.cache.get(token_info['search_id'])
        if sorted_mvs is None:
            raise MlflowException(
                "Invalid page token: search id not found or expired",
                INVALID_PARAMETER_VALUE,
            )
        start_offset = token_info['offset']
        final_offset = start_offset + max_results

        paginated_rms = sorted_mvs[start_offset: min(len(sorted_mvs), final_offset)]
        next_page_token = None
        if final_offset < len(sorted_mvs):
            next_page_token = _create_page_token(final_offset, token_info['search_id'])
        else:
            self.cache.pop(token_info['search_id'], None)
            log_msg("pop cache {} {} {} {} {} {}".format(
                token_info['search_id'], start_offset, final_offset, len(sorted_mvs), page_token, next_page_token))
        return PagedList(paginated_rms, next_page_token)

    def set_model_version_tag(self, name, version, tag):
        log_msg("set_model_version_tag {} {} {}".format(name, version, tag))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersion": _set_model_version(version),
            "Properties": _add_tag_to_properties(tag)
        }
        self._call("ModifyModelVersionProperties", req)

    def delete_model_version_tag(self, name, version, key):
        log_msg("delete_model_version_tag {} {} {}".format(name, version, key))
        [catalog_name, schema_name, model_name] = self._split_model_name(name)
        req = {
            "CatalogName": catalog_name,
            "SchemaName": schema_name,
            "ModelName": model_name,
            "ModelVersion": _set_model_version(version),
            "RemovedKeys": [_append_tag_key_prefix(key)]
        }
        self._call("ModifyModelVersionProperties", req)

    def set_registered_model_alias(self, name, alias, version):
        raise NotImplementedError("Method not implemented")

    def delete_registered_model_alias(self, name, alias):
        raise NotImplementedError("Method not implemented")

    def get_model_version_by_alias(self, name, alias):
        log_msg("get_model_version_by_alias {} {}".format(name, alias))
        return self._get_model_version_by_alias(name, alias)

    def get_model_version_download_uri(self, name, version):
        log_msg("get_model_version_download_uri {} {}".format(name, version))
        model_version = self.get_model_version(name, version)
        return model_version.source