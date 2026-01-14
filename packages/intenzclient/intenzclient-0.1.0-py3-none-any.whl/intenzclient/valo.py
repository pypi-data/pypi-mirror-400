# module imports
import typing as t
import requests
import os
import base64
import urllib3
import json, time

# imports for modules used in the package
from .resources import regions
from .resources import region_shard_override, shard_region_override
from .resources import base_endpoint
from .resources import base_endpoint_glz
from .resources import base_endpoint_local
from .resources import base_endpoint_shared

from .auth import Auth

# exceptions
from .exceptions import ResponseError, HandshakeError, LockfileError, PhaseError

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Client:
    def __init__(self, region: t.Text="na", auth: t.Optional[t.Mapping]=None):
        if auth is None:
            self.lockfile_path = os.path.join(
                os.getenv("LOCALAPPDATA"), R"Riot Games\Riot Client\Config\lockfile"
            )

        self.puuid = ""
        self.player_name = ""
        self.player_tag = ""
        self.lockfile = {}
        self.headers = {}
        self.local_headers = {}
        self.region = region
        self.shard = region
        self.auth = None
        self.client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

        if auth is not None:
            self.auth = Auth(auth)

        if region in regions:
            self.region = region
        else:
            raise ValueError(f"Invalid region, valid regions are: {regions}")

        if self.region in region_shard_override.keys():
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override.keys():
            self.region = shard_region_override[self.shard]

        self.base_url, self.base_url_glz, self.base_url_shared = self.__build_urls()

    def activate(self) -> None:
        """Activate the client and get authorization"""
        try:
            if self.auth is None:
                self.lockfile = self.__get_lockfile()
                self.puuid, self.headers, self.local_headers = self.__get_headers()

                session = self.rnet_fetch_chat_session()
                self.player_name = session["game_name"]
                self.player_tag = session["game_tag"]
            else:
                self.puuid, self.headers, self.local_headers = self.auth.authenticate()
        except:
            raise HandshakeError("Unable to activate; is VALORANT running?")

    @staticmethod
    def fetch_regions() -> t.List:
        """Fetch valid regions"""
        return regions

    def __verify_status_code(self, status_code, exceptions={}):
        """Verify that the request was successful according to exceptions"""
        if status_code in exceptions.keys():
            response_exception = exceptions[status_code]
            raise response_exception[0](response_exception[1])

    def fetch(
        self, endpoint="/", endpoint_type="pd", exceptions={}
    ) -> dict:  # exception: code: {Exception, Message}
        """Get data from a pd/glz/local endpoint"""
        data = None
        if endpoint_type in ["pd", "glz", "shared"]:
            response = requests.get(
                f'{self.base_url_glz if endpoint_type == "glz" else self.base_url if endpoint_type == "pd" else self.base_url_shared if endpoint_type == "shared" else self.base_url}{endpoint}',
                headers=self.headers,
            )

            # custom exceptions for http status codes
            self.__verify_status_code(response.status_code, exceptions)

            try:
                data = json.loads(response.text)
            except:  # as no data is set, an exception will be raised later in the method
                pass

        elif endpoint_type == "local":
            response = requests.get(
                "https://127.0.0.1:{port}{endpoint}".format(
                    port=self.lockfile["port"], endpoint=endpoint
                ),
                headers=self.local_headers,
                verify=False,
            )

            # custom exceptions for http status codes
            self.__verify_status_code(response.status_code, exceptions)

            try:
                data = response.json()
            except:  # as no data is set, an exception will be raised later in the method
                pass

        if data is None:
            raise ResponseError("Request returned NoneType")

        if "httpStatus" not in data:
            return data
        if data["httpStatus"] == 400:
            # if headers expire (i dont think they ever do but jic), refresh em!
            if self.auth is None:
                self.puuid, self.headers, self.local_headers = self.__get_headers()
            else:
                self.puuid, self.headers, self.local_headers = self.auth.authenticate()
            return self.fetch(endpoint=endpoint, endpoint_type=endpoint_type)

    def post(
        self, endpoint="/", endpoint_type="pd", json_data={}, exceptions={}
    ) -> dict:
        """Post data to a pd/glz endpoint"""
        data = None
        response = requests.post(
            f'{self.base_url_glz if endpoint_type == "glz" else self.base_url}{endpoint}',
            headers=self.headers,
            json=json_data,
        )

        # custom exceptions for http status codes
        self.__verify_status_code(response.status_code, exceptions)

        try:
            data = json.loads(response.text)
        except:
            data = None

        return data

    def put(
        self, endpoint="/", endpoint_type="pd", json_data={}, exceptions={}
    ) -> dict:
        response = requests.put(
            f'{self.base_url_glz if endpoint_type == "glz" else self.base_url}{endpoint}',
            headers=self.headers,
            data=json.dumps(json_data),
        )
        data = json.loads(response.text)

        # custom exceptions for http status codes
        self.__verify_status_code(response.status_code, exceptions)

        if data is not None:
            return data
        else:
            raise ResponseError("Request returned NoneType")

    def delete(
        self, endpoint="/", endpoint_type="pd", json_data={}, exceptions={}
    ) -> dict:
        response = requests.delete(
            f'{self.base_url_glz if endpoint_type == "glz" else self.base_url}{endpoint}',
            headers=self.headers,
            data=json.dumps(json_data),
        )
        data = json.loads(response.text)

        # custom exceptions for http status codes
        self.__verify_status_code(response.status_code, exceptions)

        if data is not None:
            return data
        else:
            raise ResponseError("Request returned NoneType")

    # --------------------------------------------------------------------------------------------------

    # PVP endpoints
    def fetch_content(self) -> t.Mapping[str, t.Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        data = self.fetch(
            endpoint="/content-service/v3/content", endpoint_type="shared"
        )
        return data

    def fetch_account_xp(self) -> t.Mapping[str, t.Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        data = self.fetch(
            endpoint=f"/account-xp/v1/players/{self.puuid}", endpoint_type="pd"
        )
        return data


    # local utility functions
    def __get_live_season(self) -> str:
        """Get the UUID of the live competitive season"""
        return self.fetch_mmr()["LatestCompetitiveUpdate"]["SeasonID"]

    def __check_puuid(self, puuid) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid

    def __check_party_id(self, party_id) -> str:
        """If party ID passed into method is None make it user's current party"""
        return self.__get_current_party_id() if party_id is None else party_id

    def __get_current_party_id(self) -> str:
        """Get the user's current party ID"""
        party = self.party_fetch_player()
        return party["CurrentPartyID"]

    def __coregame_check_match_id(self, match_id) -> str:
        """Check if a match id was passed into the method"""
        return self.coregame_fetch_player()["MatchID"] if match_id is None else match_id

    def __pregame_check_match_id(self, match_id) -> str:
        return self.pregame_fetch_player()["MatchID"] if match_id is None else match_id   

    def __build_urls(self) -> str:
        """Generate URLs based on region/shard"""
        base_url = base_endpoint.format(shard=self.shard)
        base_url_glz = base_endpoint_glz.format(shard=self.shard, region=self.region)
        base_url_shared = base_endpoint_shared.format(shard=self.shard)
        return base_url, base_url_glz, base_url_shared

    def __get_headers(self) -> t.Tuple[t.Text, t.Mapping[t.Text, t.Any]]:
        """Get authorization headers to make requests"""
        try:
            if self.auth is None:
                return self.__get_auth_headers()
            puuid, headers, _ = self.auth.authenticate()
            headers["X-Riot-ClientPlatform"] = (self.client_platform,)
            headers["X-Riot-ClientVersion"] = self.__get_current_version()
            return puuid, headers, None

        except Exception as e:
            print(e)
            raise HandshakeError("Unable to get headers; is VALORANT running?")

    def __get_auth_headers(self) -> t.Tuple[t.Text, t.Mapping[t.Text, t.Any]]: 
        # headers for pd/glz endpoints
        local_headers = {
            "Authorization": (
                "Basic "
                + base64.b64encode(
                    ("riot:" + self.lockfile["password"]).encode()
                ).decode()
            )
        }
        response = requests.get(
            "https://127.0.0.1:{port}/entitlements/v1/token".format(
                port=self.lockfile["port"]
            ),
            headers=local_headers,
            verify=False,
        )
        entitlements = response.json()
        puuid = entitlements["subject"]
        headers = {
            "Authorization": f"Bearer {entitlements['accessToken']}",
            "X-Riot-Entitlements-JWT": entitlements["token"],
            "X-Riot-ClientPlatform": self.client_platform,
            "X-Riot-ClientVersion": self.__get_current_version(),
        }
        return puuid, headers, local_headers

    def __get_current_version(self) -> str:
        data = requests.get("https://valorant-api.com/v1/version")
        data = data.json()["data"]
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"  # return formatted version string

    def __get_lockfile(self) -> t.Optional[t.Mapping[str, t.Any]]:
        try:
            with open(self.lockfile_path) as lockfile:
                data = lockfile.read().split(":")
                keys = ["name", "PID", "port", "password", "protocol"]
                return dict(zip(keys, data))
        except:
            raise LockfileError("Lockfile not found")
        

    def in_agent_select(self):
        """Checks if user is currently is in the agent select and returns MatchID"""
        try:
            data = self.fetch(
                endpoint=f"/pregame/v1/players/{self.puuid}",
                endpoint_type="glz",
                exceptions={404: [PhaseError, "You are not in a pre-game"]},
            )
            if data and data.get("MatchID"):
                return data.get("MatchID")
        except PhaseError:
            return False
        except Exception as e:
            return False
        return False
    
    def is_ingame(self):
        """Checks if User is currently in a game and returns MatchID"""
        try:
            data = self.fetch(
                endpoint=f"/core-game/v1/players/{self.puuid}",
                endpoint_type="glz",
                exceptions={404: [PhaseError, "You are not in a core-game"]},
            )
            if data and data.get("MatchID"):
                return data.get("MatchID")
        except PhaseError:
            return False
        except Exception as e:
            return False
        return False
    
    def is_lobby(self):
        """Checks if User is currently in the lobby"""
        if (not self.in_agent_select()) and (not self.is_ingame()):
            return True
        return False
    
    def party_id(self):
        """Get the user's current party ID"""
        data = self.fetch(
            endpoint=f"/parties/v1/players/{self.puuid}", endpoint_type="glz"
        )
        return data["CurrentPartyID"]
    
    
    def select_agent(self, agent_id):
        """Selects agent"""
        match_id = self.in_agent_select()
        if match_id:
            data = self.post(
                endpoint=f"/pregame/v1/matches/{match_id}/select/{agent_id}",
                endpoint_type="glz",
                exceptions={404: [PhaseError, "You are not in a pre-game"]},
            )
            return data
        else:
            return False

    def lock_agent(self, agent_id):
        """Locks agent"""
        match_id = self.in_agent_select()
        if match_id:
            data = self.post(
                endpoint=f"/pregame/v1/matches/{match_id}/lock/{agent_id}",
                endpoint_type="glz",
                exceptions={404: [PhaseError, "You are not in a pre-game"]},
            )
            return data
        else:
            return False
        
    def instalock_agent(self, agent_id):
        """Selects and locks agent instantly"""
        if self.in_agent_select():
            time.sleep(4)
            self.select_agent(agent_id)
            time.sleep(2)
            self.lock_agent(agent_id)
            return True
        else:
            return False

    def change_queue(self, queue_id: t.Text) -> t.Mapping[str, t.Any]:
        """Changes matchmaking queue"""
        party_id = self.__get_current_party_id()
        data = self.post(
            endpoint=f"/parties/v1/parties/{party_id}/queue",
            endpoint_type="glz",
            json_data={"queueID": queue_id},
        )
        return data

    def start_custom_game(self) -> t.Mapping[str, t.Any]:
        """Starts custom game"""
        party_id = self.__get_current_party_id()
        data = self.post(
            endpoint=f"/parties/v1/parties/{party_id}/startcustomgame",
            endpoint_type="glz",
        )
        return data

    def enter_matchmaking(self) -> t.Mapping[str, t.Any]:
        """Enters matchmaking"""
        party_id = self.__get_current_party_id()
        data = self.post(
            endpoint=f"/parties/v1/parties/{party_id}/matchmaking/join",
            endpoint_type="glz",
        )
        return data

    def leave_matchmaking(self) -> t.Mapping[str, t.Any]:
        """Leaves matchmaking"""
        party_id = self.__get_current_party_id()
        data = self.post(
            endpoint=f"/parties/v1/parties/{party_id}/matchmaking/leave",
            endpoint_type="glz",
        )
        return data
    
    def owned_items(
        self, item_type: t.Text = "e7c63390-eda7-46e0-bb7a-a6abdacd2433"
    ) -> t.Mapping[str, t.Any]:
        """
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in client.fetch_content() to know what items are owned

        NOTE: uuid to item type
        "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "skin_level",
        "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "skin_chroma",
        "01bb38e1-da47-4e6a-9b3d-945fe4655707": "agent",
        "f85cb6f7-33e5-4dc8-b609-ec7212301948": "contract_definition",
        "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "buddy",
        "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475": "spray",
        "3f296c07-64c3-494c-923b-fe692a4fa1bd": "player_card",
        "de7caa6b-adf7-4588-bbd1-143831e786c6": "player_title",
        """
        data = self.fetch(
            endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}",
            endpoint_type="pd",
        )
        return data

    def skin_map():
        try:
            response = requests.get("https://valorant-api.com/v1/weapons/skins")
            data = response.json()
            return data
        except Exception as e:
            return False
        

    def item_prices(self) -> t.Mapping[str, t.Any]:
        """Get prices for all store items"""
        data = self.fetch("/store/v1/offers/", endpoint_type="pd")
        return data

    def store_items(self) -> t.Mapping[str, t.Any]:
        """Get the currently available items in the store"""
        data = self.fetch(f"/store/v2/storefront/{self.puuid}", endpoint_type="pd")
        return data

    def wallet(self) -> t.Mapping[str, t.Any]:
        """Get amount of Valorant points Radianite and Kingdom Credits the player has"""
        data = self.fetch(f"/store/v1/wallet/{self.puuid}", endpoint_type="pd")
        return data