from pathlib import Path
import shutil

import rich

from hatch.publish.plugin.interface import PublisherInterface

# SEE A PUBLISHER EXAMPLE HERE:
# https://github.com/trash-panda-v91-beta/hatch-aws-publisher/blob/main/README.md


class TGZRAssetPublisher(PublisherInterface):
    PLUGIN_NAME = "tgzr-pipeline-asset"

    def publish(self, artifacts: list, options: dict):
        project_config = self.project_config | options
        rich.print("TGZR Asset Publisher Config:", project_config)
        rich.print("Artifacts:", artifacts)

        publish_to = project_config.get("publish_to", "review")
        repos = project_config.get("repos", {})
        target = repos.get(publish_to)
        if target is None:
            known_repos = "\n".join(
                [f"{k:>10}:{v}" for k, v in project_config.get("repos", {}).items()]
            )
            rich.print(
                f"\n\n[bold red]ERROR[/bold red]: Could not publish to {publish_to!r}, no repo with this name is defined.\n"
                "Known repos are: \n"
                f"{known_repos}\n\n"
                "Provide another repo name with --o publish_to=repo_name, or add this in pyproject.toml:\n"
                "\n"
                "[tool.hatch.publish.tgzr-asset]\n"
                f'{publish_to}="path/to/the/folder"\n'
            )
            return
        print(f"Publishing to repo {target}")
        target = Path(target)
        target.mkdir(exist_ok=True, parents=True)

        for item in artifacts:
            artifact = Path(item)
            name = artifact.name
            target_path = target / name
            if target_path.exists():
                print("  Skipping existing target:", target_path)
                continue
            print("  Copying to", target_path)
            shutil.copy2(artifact, target_path)
