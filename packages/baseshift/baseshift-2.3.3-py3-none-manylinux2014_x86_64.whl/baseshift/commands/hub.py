import json
import logging
from time import sleep

from .. import utils
from .. import client  # v2 API only (JWT auth required)
from .base import BaseCommand

logger = logging.getLogger(__name__)


class HubCommand(BaseCommand):
    def add_arguments(self, parser):
        hub_subparsers = parser.add_subparsers(dest="action", required=True)

        # Create hub/environment
        parser_create = hub_subparsers.add_parser(
            "create", help="Create a new hub/environment"
        )
        parser_create.add_argument(
            "--name",
            required=True,
            help="Name of the hub/environment",
        )
        parser_create.add_argument(
            "--dubUuids",
            required=True,
            help="Comma-separated list of Dub UUIDs to add to the hub",
        )
        parser_create.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )
        parser_create.add_argument(
            "--schedule",
            required=False,
            default="never",
            choices=["never", "daily", "weekly", "monthly"],
            help="Snapshot schedule for the hub",
        )

        # Hub status
        parser_status = hub_subparsers.add_parser(
            "status", help="Get hub/environment status"
        )
        parser_status.add_argument(
            "--envUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Hub/Environment (CLI > BASESHIFT_ENV_UUID > config)",
        )
        # Hub snapshot
        parser_snapshot = hub_subparsers.add_parser(
            "snapshot", help="Create or check hub/environment snapshot"
        )
        parser_snapshot.add_argument(
            "--envUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Hub/Environment (CLI > BASESHIFT_ENV_UUID > config)",
        )
        parser_snapshot.add_argument(
            "--prepareOnly",
            action="store_true",
            help="Only prepare the snapshot without creating it",
        )
        parser_snapshot.add_argument(
            "--tag",
            required=False,
            help="Optional tag for the snapshot",
        )
        parser_snapshot.add_argument(
            "--snapshotUuid",
            required=False,
            type=utils.regex_type_uuid,
            help="UUID of snapshot to check status (for GET operation)",
        )
        parser_snapshot.add_argument(
            "--wait",
            action="store_true",
            help="Wait for snapshot to complete (only for POST)",
        )

        # List dubs in hub
        parser_list_dubs = hub_subparsers.add_parser(
            "list_dubs", help="List dubs in hub/environment"
        )
        parser_list_dubs.add_argument(
            "--envUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Hub/Environment (CLI > BASESHIFT_ENV_UUID > config)",
        )
        # Add dub to hub
        parser_add_dub = hub_subparsers.add_parser(
            "add_dub", help="Add a dub to hub/environment"
        )
        parser_add_dub.add_argument(
            "--envUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Hub/Environment (CLI > BASESHIFT_ENV_UUID > config)",
        )
        parser_add_dub.add_argument(
            "--dubUuid",
            required=True,
            type=utils.regex_type_uuid,
            help="Uuid of Dub to add",
        )
        # Remove dub from hub
        parser_remove_dub = hub_subparsers.add_parser(
            "remove_dub", help="Remove a dub from hub/environment"
        )
        parser_remove_dub.add_argument(
            "--envUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Hub/Environment (CLI > BASESHIFT_ENV_UUID > config)",
        )
        parser_remove_dub.add_argument(
            "--dubUuid",
            required=True,
            type=utils.regex_type_uuid,
            help="Uuid of Dub to remove",
        )
        pass  # No additional arguments needed

    def run(self, args, server):
        if args.action == "create":
            self.create_hub(args, server)
        elif args.action == "status":
            self.hub_status(args, server)
        elif args.action == "snapshot":
            self.hub_snapshot(args, server)
        elif args.action == "list_dubs":
            self.list_dubs(args, server)
        elif args.action == "add_dub":
            self.add_dub(args, server)
        elif args.action == "remove_dub":
            self.remove_dub(args, server)

    def create_hub(self, args, server):
        try:
            org_token = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token):
                logger.error(f"Invalid Organization Token format: {org_token}")
                print(
                    f"Error: Invalid Organization Token format: {org_token}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in create hub: {e}")
            print(f"Error: {e}")
            return

        # Parse comma-separated dub UUIDs
        try:
            dub_uuids = [uuid.strip() for uuid in args.dubUuids.split(",")]
            for uuid in dub_uuids:
                if not utils.is_valid_uuid(uuid):
                    logger.error(f"Invalid Dub UUID format: {uuid}")
                    print(f"Error: Invalid Dub UUID format: {uuid}")
                    return
        except Exception as e:
            logger.error(f"Error parsing Dub UUIDs: {e}")
            print(f"Error: Invalid Dub UUIDs format. Use comma-separated list.")
            return

        try:
            response = client.create_hub_api_sync(
                hub_name=args.name,
                dub_uuid_list=dub_uuids,
                host=server,
                org_token=org_token,
                schedule=args.schedule,
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()
            print(f"Hub/Environment created successfully!")
            print(f"Environment ID: {result.get('env_id')}")

        except Exception as e:
            logger.exception("Error creating hub: " + str(e))
            print(f"Error creating hub: {e}")

    def hub_status(self, args, server):
        try:
            env_uuid = utils.get_config_value(
                args.envUuid, "BASESHIFT_ENV_UUID", "envUuid", required=True
            )
            if not utils.is_valid_uuid(env_uuid):
                logger.error(f"Invalid Environment UUID format: {env_uuid}")
                print(
                    f"Error: Invalid Environment UUID format: {env_uuid}. Please check CLI, BASESHIFT_ENV_UUID, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in hub status: {e}")
            print(f"Error: {e}")
            return

        try:
            response = client.hub_status_api_sync(
                env_uuid=env_uuid,
                host=server,
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()
            print(f"Hub/Environment Status: {result.get('env_status')}")

            if result.get("last_snapshot_id"):
                print(f"\nLast Snapshot:")
                print(f"  ID: {result.get('last_snapshot_id')}")
                print(f"  Name: {result.get('last_snapshot_name')}")
                print(f"  Created: {result.get('last_snapshot_created_at')}")

            if result.get("ongoing_snapshot_id"):
                print(f"\nOngoing Snapshot ID: {result.get('ongoing_snapshot_id')}")

            if result.get("dubs_status"):
                print(f"\nDubs Status:")
                for dub_name, dub_info in result["dubs_status"].items():
                    print(
                        f"  {dub_name}: {dub_info.get('status')} (ID: {dub_info.get('id')})"
                    )

        except Exception as e:
            logger.exception("Error getting hub status: " + str(e))
            print(f"Error getting hub status: {e}")

    def hub_snapshot(self, args, server):
        try:
            env_uuid = utils.get_config_value(
                args.envUuid, "BASESHIFT_ENV_UUID", "envUuid", required=True
            )
            if not utils.is_valid_uuid(env_uuid):
                logger.error(f"Invalid Environment UUID format: {env_uuid}")
                print(
                    f"Error: Invalid Environment UUID format: {env_uuid}. Please check CLI, BASESHIFT_ENV_UUID, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in hub snapshot: {e}")
            print(f"Error: {e}")
            return

        # Determine if this is a GET (status check) or POST (create snapshot)
        method = "GET" if args.snapshotUuid else "POST"

        try:
            response = client.hub_snapshot_api_sync(
                env_uuid=env_uuid,
                host=server,
                method=method,
                prepare_only=args.prepareOnly if method == "POST" else False,
                tag=args.tag if hasattr(args, "tag") else None,
                snapshot_uuid=(
                    args.snapshotUuid if hasattr(args, "snapshotUuid") else None
                ),
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()

            if method == "GET":
                # Status check response
                print(f"Environment Status: {result.get('env_status')}")
                print(f"Snapshot ID: {result.get('snapshot_id')}")
                print(f"Snapshot Name: {result.get('name')}")

                if result.get("dubs_status"):
                    print(f"\nDubs Snapshot Status:")
                    for dub_name, dub_info in result["dubs_status"].items():
                        print(
                            f"  {dub_name}: {dub_info.get('snapshot_status')} (ID: {dub_info.get('id')})"
                        )
            else:
                # Create/prepare snapshot response
                if args.prepareOnly:
                    print(f"Hub preparation status: {result.get('status')}")
                else:
                    snapshot_id = result.get("snapshot_id") or result.get("uuid")
                    print(f"Creating snapshot {snapshot_id}", flush=True)

                    if args.wait:
                        print("Waiting for snapshot to complete", end="", flush=True)
                        snapshot_ready = False
                        while not snapshot_ready:
                            sleep(2)
                            print(".", end="", flush=True)

                            # Check snapshot status
                            status_response = client.hub_snapshot_api_sync(
                                env_uuid=env_uuid,
                                host=server,
                                method="GET",
                                snapshot_uuid=snapshot_id,
                            )

                            if status_response.status_code == 200:
                                status_result = status_response.json()
                                env_status = status_result.get("env_status")

                                # Check if all dubs are ready
                                dubs_status = status_result.get("dubs_status", {})
                                all_ready = all(
                                    dub.get("snapshot_status") == "READY"
                                    for dub in dubs_status.values()
                                )

                                if env_status == "READY" and all_ready:
                                    snapshot_ready = True

                        print(f"\nSnapshot {snapshot_id} completed successfully")

        except Exception as e:
            logger.exception("Error with hub snapshot: " + str(e))
            print(f"Error with hub snapshot: {e}")

    def list_dubs(self, args, server):
        try:
            env_uuid = utils.get_config_value(
                args.envUuid, "BASESHIFT_ENV_UUID", "envUuid", required=True
            )
            if not utils.is_valid_uuid(env_uuid):
                logger.error(f"Invalid Environment UUID format: {env_uuid}")
                print(
                    f"Error: Invalid Environment UUID format: {env_uuid}. Please check CLI, BASESHIFT_ENV_UUID, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in list dubs: {e}")
            print(f"Error: {e}")
            return

        try:
            response = client.hub_dubs_api_sync(
                env_uuid=env_uuid,
                host=server,
                method="GET",
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()

            if result:
                print("Dubs in hub/environment:")
                for dub_name, dub_info in result.items():
                    print(f"  {dub_name}: {dub_info.get('id')}")
            else:
                print("No dubs in this hub/environment")

        except Exception as e:
            logger.exception("Error listing dubs: " + str(e))
            print(f"Error listing dubs: {e}")

    def add_dub(self, args, server):
        try:
            env_uuid = utils.get_config_value(
                args.envUuid, "BASESHIFT_ENV_UUID", "envUuid", required=True
            )
            if not utils.is_valid_uuid(env_uuid):
                logger.error(f"Invalid Environment UUID format: {env_uuid}")
                print(
                    f"Error: Invalid Environment UUID format: {env_uuid}. Please check CLI, BASESHIFT_ENV_UUID, or config file."
                )
                return

            if not utils.is_valid_uuid(args.dubUuid):
                logger.error(f"Invalid Dub UUID format: {args.dubUuid}")
                print(f"Error: Invalid Dub UUID format: {args.dubUuid}")
                return

        except ValueError as e:
            logger.error(f"Configuration error in add dub: {e}")
            print(f"Error: {e}")
            return

        try:
            response = client.hub_dubs_api_sync(
                env_uuid=env_uuid,
                host=server,
                method="POST",
                dub_uuid=args.dubUuid,
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()
            print(f"Dub {args.dubUuid} added to hub/environment successfully")
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))

        except Exception as e:
            logger.exception("Error adding dub: " + str(e))
            print(f"Error adding dub: {e}")

    def remove_dub(self, args, server):
        try:
            env_uuid = utils.get_config_value(
                args.envUuid, "BASESHIFT_ENV_UUID", "envUuid", required=True
            )
            if not utils.is_valid_uuid(env_uuid):
                logger.error(f"Invalid Environment UUID format: {env_uuid}")
                print(
                    f"Error: Invalid Environment UUID format: {env_uuid}. Please check CLI, BASESHIFT_ENV_UUID, or config file."
                )
                return

            if not utils.is_valid_uuid(args.dubUuid):
                logger.error(f"Invalid Dub UUID format: {args.dubUuid}")
                print(f"Error: Invalid Dub UUID format: {args.dubUuid}")
                return

        except ValueError as e:
            logger.error(f"Configuration error in remove dub: {e}")
            print(f"Error: {e}")
            return

        try:
            response = client.hub_dubs_api_sync(
                env_uuid=env_uuid,
                host=server,
                method="DELETE",
                dub_uuid=args.dubUuid,
            )
            if response.status_code in [400, 403, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.text)
                print(f"Error: {response.text}")
                return

            result = response.json()
            print(f"Dub {args.dubUuid} removed from hub/environment successfully")
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))

        except Exception as e:
            logger.exception("Error removing dub: " + str(e))
            print(f"Error removing dub: {e}")
