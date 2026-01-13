import urllib.parse
import json
import os.path
from .brand_name_enum import BrandName
from .environment_name_enum import EnvironmentName

SERVERLESS_OFFLINE_DEFAULT_PORT = 3000
REACTJS_APP_DEFAULT_PORT = 5173
TIMELINE_DEFAULT_PORT = 8080
STAGE = "local"


class OurUrl:
    # static dict for domain mapping
    base_url = "execute-api.us-east-1.amazonaws.com"
    # TODO: get those automatically.
    domain_mapping = {
        "auth.dvlp1.circ.zone": "i4wp5o2381",
        "auth.play1.circ.zone": "efwzjj0uz2",  # 'nmxjjpyrv9',
        "user-registration.dvlp1.circ.zone": "lczo7l194b",
        "user-registration.play1.circ.zone": "t3tnkh0r64",
        "gender-detection.dvlp1.circ.zone": "353sstqmj5",  # TODO: update
        "gender-detection.play1.circ.zone": "353sstqmj5",
        "group.dvlp1.circ.zone": "2mvpuqbhh1",
        "group.play1.circ.zone": "ly0jegwkib",
        "group-profile.dvlp1.circ.zone": "dot2ynvxwl",
        "group-profile.play1.circ.zone": "wh1toflnza",
        "marketplace-goods.play1.circ.zone": "vcev0rrt01",
        "logger.dvlp1.circ.zone": "t91y4nxsye",
        "logger.play1.circ.zone": " q6lmvupsaa",  # 'fsujmjyfal',
        # 'event.play1.circ.zone': 'p89mpsr5m1',
        # 'event.play1.circ.zone': 'x8ql0j9cwf',
        # "event.play1.circ.zone": "ex2g453qsj",
        # "event.play1.circ.zone": "968i3rfj1g",
        "event.play1.circ.zone": "ex2g453qsj",
        "event.dvlp1.circ.zone": "wbq5liyk63",  # TODO update
        "storage.play1.circ.zone": "wbq5liyk63",  # TODO update once passed in GHA
        "storage.dvlp1.circ.zone": "wbq5liyk63",  # TODO update once passed in GHA
        "smartlink.play1.circ.zone": "faz4k77vi5",
        "smartlink.dvlp1.circ.zone": "71xv3yng8e",
        "dialogWorkflow.play1.circ.zone": "0fk85378x2",
        # "dialogWorkflow.play1.circ.zone": "hyca8eo3jd",
        "dialogWorkflow.dvlp1.circ.zone": "xoonx24zbg",  # TODO: update
        # 'websocket.dvlp1.circ.zone': 'ws://23.22.217.199:8080',
        # 'websocket.play1.circ.zone': 'ws://23.22.217.199:8080',
    }

    @staticmethod  # TODO: should we get from .env if not given?
    def base_domain(
        *, brand_name: str = BrandName.CIRCLEZ.value, environment_name: str
    ) -> str:
        """
        Return the base domain based on the input environment.

        Parameters:
            brand_name (string): Actual brand name.
            environment_name (string): Desired environment name

        Return:
            A string that represents the base domain of a given environment name.
        """
        if brand_name == BrandName.CIRCLEZ.value:
            if environment_name == EnvironmentName.DVLP1.value:
                base_domain = "dvlp1.circ.zone"
            elif environment_name == EnvironmentName.PLAY1.value:
                base_domain = "play1.circ.zone"
            elif environment_name == EnvironmentName.PROD1.value:
                base_domain = "circlez.ai"
            elif environment_name == EnvironmentName.LOCAL.value:
                base_domain = "localhost"
            else:
                message = f"Invalid {environment_name=} in {brand_name=}"
                raise ValueError(message)
            return base_domain
        else:
            raise ValueError('Invalid BRAND_NAME "' + brand_name + '"')

    @staticmethod
    def app_url(
        *,
        brand_name: str = BrandName.CIRCLEZ.value,
        environment_name: str,
        port: int = REACTJS_APP_DEFAULT_PORT,
    ) -> str:
        # https://github.com/circles-zone/url-remote-typescript-package/blob/dev/url-remote-typescript-package/src/index.ts#L91
        if brand_name == BrandName.CIRCLEZ.value:
            if environment_name == EnvironmentName.LOCAL.value:
                url = f"localhost:{port}"
            elif environment_name == EnvironmentName.PLAY1_S3_UNSECURED.value:
                url = "http://circlez-user-reactjs-frontend-unsecured-s3.play1.circ.zone.s3-website-us-east-1.amazonaws.com/"
            elif environment_name == EnvironmentName.PLAY1_S3_SECURED.value:
                url = "http://circles-user-reactjs-frontend.play1.circ.zone.s3-website-us-east-1.amazonaws.com/"
            elif environment_name == EnvironmentName.PLAY1_CLOUDFRONT.value:
                url = "http://d1yvwaumwtbd49.cloudfront.net/"
            elif environment_name == EnvironmentName.PLAY1.value:
                url = "http://play1.circ.zone/"
            elif environment_name == EnvironmentName.PLAY1_CIRC_ZONE_SSL.value:
                url = "https://play1.circ.zone/"
            elif environment_name == EnvironmentName.DVLP1.value:
                # url = "https://d2f9rjvjaf75eo.cloudfront.net/"
                url = "https://circles-user-reactjs-frontend.dvlp1.circ.zone.s3-website-us-east-1.amazonaws.com/"
            elif environment_name == EnvironmentName.PROD1.value:
                url = "https://circlez.ai/"
            else:
                raise ValueError("Invalid environment name")
            return url
        else:
            raise ValueError('Invalid BRAND_NAME "' + brand_name + '"')

    @staticmethod  # TODO: Use enums - brand_name: BrandName, same for all
    def endpoint_url(
        brand_name: str,
        environment_name: str,
        component_name: str,
        entity_name: str,
        version: int,
        action_name: str,
        path_parameters: dict = None,
        query_parameters: dict = None,
        default_port: int = SERVERLESS_OFFLINE_DEFAULT_PORT,
    ) -> str:
        """
        Function that generate a URL with the format:
            "https://{direct_domain}/{environment_name}/api/v{version}/{entity}/{action}/{parameters}"

        Parameters:
            brand_name (string): Actual brand name.
            environment_name (string): Desired environment name.
            component_name (string): Desired component.
            entity_name (string): Desired entity.
            version (integer): Version.
            action_name (string): Desired action.
            path_parameters (dictionary): A dictionary representing the path parameters with their values.
            query_parameters (dictionary): A dictionary representing the query parameters with their values.

        Return:
            A string that represent the desired endpoint url based on input.

        """
        environment_name, port = OurUrl.get_actual_environment_and_port(
            component_name, environment_name, default_port)

        base_url = OurUrl._base_url_builder(
            component_name=component_name,
            brand_name=brand_name,
            environment_name=environment_name,
            version=version,
            entity_name=entity_name,
            action_name=action_name,
        )
        print(f"base_url: {base_url}")

        if path_parameters:
            path_params_string = "/".join(
                [urllib.parse.quote_plus(str(val))
                 for val in path_parameters.values()]
            )
            url_with_path_params = f"{base_url}/{path_params_string}"
        else:
            url_with_path_params = base_url

        if query_parameters:
            query_params_string = "&".join(
                [
                    f"{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(str(value))}"
                    for key, value in query_parameters.items()
                ]
            )
            url_with_query_params = f"{url_with_path_params}?{query_params_string}"
        else:
            url_with_query_params = url_with_path_params

        # TODO: send params
        new_url = OurUrl._convert_to_direct_url(
            direct_url=url_with_query_params)
        return new_url

    @staticmethod
    def _base_url_builder(
        *,
        component_name: str,
        brand_name: str = BrandName.CIRCLEZ.value,
        environment_name: str,
        version: int,
        entity_name: str,
        action_name: str,
    ) -> str:
        """
        Function that generate the basic direct url with the format:
            "https://{direct_domain}/{environment_name}/api/v{version}/{entity}/{action}"

        Parameters:
            brand_name (string): Actual brand name.
            environment_name (string): Desired environment name.
            component_name (string): Desired component.
            version (integer): Version.
            action_name (string): Desired action.

        Return:
            A string representing direct url after mapping out the domain.
        """
        if environment_name != EnvironmentName.LOCAL.value:
            print("not local")
            print(version)
            base_domain = f"{component_name}.{OurUrl.base_domain(brand_name=brand_name, environment_name=environment_name)}"
            try:
                direct_domain = OurUrl.domain_mapping[base_domain]
            except KeyError:
                # Handle the case when the base_domain is not found in the domain_mapping
                raise ValueError(
                    f"Domain mapping not found for '{base_domain}' in brand '{brand_name}' and environment" +
                    f"'{environment_name}' please update our_url.py domain_mapping data structure."
                )
            direct_url = f"https://{direct_domain}.{OurUrl.base_url}/{environment_name}/api/v{version}/{entity_name}/{action_name}"  # noqa: E501
        else:
            print(version)
            print(f"component:{component_name} in local")
            direct_domain = "localhost"
            direct_url = f"http://{direct_domain}:{SERVERLESS_OFFLINE_DEFAULT_PORT}/{STAGE}/api/v{version}/{entity_name}/{action_name}"  # noqa: E501
        return direct_url

    @staticmethod
    def _convert_to_direct_url(
        *, direct_url: str, path_parameters: dict = None, query_parameters: dict = None
    ) -> str:
        """
        Function that convert the base url to direct url.

        Parameters:
            direct_url (string): The direct url after mapping the domain from the base domain.
            path_parameters (dictionary): A dictionary representing desired path parameters.
            query_parameters (dictionary): A dictionary representing desired query parameters.

        Return:
            A string representing the final url after adding all the parameters to the direct url.
        """
        if path_parameters:
            for key, value in path_parameters.items():
                direct_url = direct_url.replace(f"{{{key}}}", value)

        path_params_string = (
            "/".join(
                urllib.parse.quote_plus(str(value))
                for value in path_parameters.values()
            )
            if path_parameters
            else ""
        )
        url_with_path_params = (
            f"{direct_url}/{path_params_string}" if path_params_string else direct_url
        )

        if query_parameters:
            query_params_string = "&".join(
                f"{urllib.parse.quote_plus(str(key))}={urllib.parse.quote_plus(str(value))}"
                for key, value in query_parameters.items()
            )
            url_with_query_params = f"{url_with_path_params}?{query_params_string}"
        else:
            url_with_query_params = url_with_path_params

        return url_with_query_params

    def get_actual_environment_and_port(component_name, environment_name, default_port):
        file_name = 'component.json'
        # TODO Add support to get the component.json file from COMPONENT_CONFIGURATION_JSON_PATH
        # TODO Validate the component.json file format
        if os.path.isfile(path=file_name):
            path = file_name
        elif os.path.isfile(path=f"../{file_name}"):
            path = f"../{file_name}"
        else:
            print(f"File {file_name} not found")
            return environment_name, default_port

        print(f"File {path} found")
        with open(path) as f:
            data = json.load(f)
            if component_name in data:
                print(f"Component {component_name} found")
                environment_name = data[component_name]["environmentName"]
                if "port" in data[component_name]:
                    port = data[component_name]["port"]
                else:
                    port = default_port
                return environment_name, port
            else:
                print(f"Component {component_name} not found")
                return environment_name, default_port
