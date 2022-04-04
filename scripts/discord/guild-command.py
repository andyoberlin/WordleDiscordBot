import requests
from dataclasses import dataclass


@dataclass()
class GuildCommandApi:
    """
    Api for updating commands for a specific guild. This is to be used for rapid testing.
    Taken from: https://discord.com/developers/docs/interactions/application-commands#making-a-guild-command
    """
    applicationId: str
    guildId: str
    applicationToken: str

    def create(self):
        url = "https://discord.com/api/v8/applications/{applicationId}/guilds/{guildId}/commands".format(
            applicationId=self.applicationId, guildId=self.guildId)

        # This is an example USER command, with a type of 2
        json = {
            "name": "High Five",
            "type": 2
        }

        # or a client credentials token for your app with the applications.commands.update scope
        headers = {
            "Authorization": "Bearer <my_credentials_token>"
        }

        result = requests.post(url, headers=headers, json=json)
