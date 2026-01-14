import collections.abc
import typing as tp

from xmanager import xm

from xm_slurm import api


class SlurmContextArtifacts(collections.abc.MutableMapping[str, str]):
    def __init__(
        self,
        owner: xm.Experiment | xm.ExperimentUnit,
        *,
        artifacts: tp.Sequence[api.models.Artifact],
    ):
        self._data = {artifact.name: artifact.uri for artifact in artifacts}
        self._owner = owner
        self._create_task = self._owner._create_task

    def add(self, name: str, uri: str) -> None:
        artifact = api.models.Artifact(name=name, uri=uri)
        match self._owner:
            case xm.Experiment():
                api.client().insert_experiment_artifact(self._owner.experiment_id, artifact)
            case xm.WorkUnit():
                api.client().insert_work_unit_artifact(
                    self._owner.experiment_id, self._owner.work_unit_id, artifact
                )

        self._data[name] = uri

    def remove(self, name: str) -> None:
        match self._owner:
            case xm.Experiment():
                api.client().delete_experiment_artifact(self._owner.experiment_id, name)
            case xm.WorkUnit():
                api.client().delete_work_unit_artifact(
                    self._owner.experiment_id, self._owner.work_unit_id, name
                )

    def __setitem__(self, name: str, uri: str) -> None:
        self.add(name, uri)

    def __delitem__(self, name: str) -> None:
        self.remove(name)

    def __getitem__(self, name: str) -> str:
        return self._data[name]

    def __iter__(self) -> tp.Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class SlurmExperimentAnnotationTags(collections.abc.MutableSet[str]):
    def __init__(self, experiment: xm.Experiment, *, tags: tp.Iterable[str]):
        self._experiment = experiment
        # Use a dict to ensure order is preserved
        self._tags = dict.fromkeys(tags)

    def add(self, tag: str) -> None:
        self._tags[tag] = None
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(tags=list(self._tags)),
        )

    def remove(self, tag: str) -> None:
        self.discard(tag)

    def discard(self, tag: str) -> None:
        self._tags.pop(tag)
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(tags=list(self._tags)),
        )

    def __contains__(self, tag: str) -> bool:
        return tag in self._tags

    def __iter__(self) -> tp.Iterator[str]:
        return iter(self._tags)

    def __len__(self) -> int:
        return len(self._tags)


class SlurmExperimentUnitMetadataContext:
    def __init__(
        self,
        experiment_unit: xm.ExperimentUnit,
        *,
        artifacts: SlurmContextArtifacts,
    ):
        self._experiment_unit = experiment_unit
        self._artifacts = artifacts

    @property
    def artifacts(self) -> SlurmContextArtifacts:
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts: SlurmContextArtifacts) -> None:
        del artifacts
        raise ValueError("The artifacts object is immutable.")


class SlurmExperimentContextAnnotations:
    def __init__(
        self,
        experiment: xm.Experiment,
        *,
        title: str,
        tags: set[str] | None = None,
        description: str | None = None,
        note: str | None = None,
    ):
        self._experiment = experiment
        self._create_task = self._experiment._create_task
        self._title = title
        self._tags = SlurmExperimentAnnotationTags(experiment, tags=tags or [])
        self._description = description or ""
        self._note = note or ""

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(title=value),
        )

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(description=value),
        )

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, value: str) -> None:
        self._note = value
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(note=value),
        )

    @property
    def tags(self) -> SlurmExperimentAnnotationTags:
        return self._tags

    @tags.setter
    def tags(self, tags: tp.Iterable[str]) -> None:
        self._tags = SlurmExperimentAnnotationTags(self._experiment, tags=tags)
        api.client().update_experiment(
            self._experiment.experiment_id,
            api.models.ExperimentPatch(tags=list(self._tags)),
        )


class SlurmExperimentMetadataContext:
    def __init__(
        self,
        experiment: xm.Experiment,
        *,
        annotations: SlurmExperimentContextAnnotations,
        artifacts: SlurmContextArtifacts,
    ):
        self._experiment = experiment
        self._annotations = annotations
        self._artifacts = artifacts

        self._graphviz_config = None
        self._python_config = None

    @property
    def annotations(self) -> SlurmExperimentContextAnnotations:
        return self._annotations

    @annotations.setter
    def annotations(self, annotations: SlurmExperimentContextAnnotations) -> None:
        del annotations
        raise ValueError("The annotations object is immutable.")

    @property
    def artifacts(self) -> SlurmContextArtifacts:
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts: SlurmContextArtifacts) -> None:
        del artifacts
        raise ValueError("The artifacts object is immutable.")

    @property
    def graphviz_config(self) -> str | None:
        return self._graphviz_config

    @graphviz_config.setter
    def graphviz_config(self, config: str | None) -> None:
        self._graphviz_config = config
        match config:
            case None:
                api.client().delete_experiment_config_artifact(
                    self._experiment.experiment_id, "GRAPHVIZ"
                )
            case str():
                api.client().insert_experiment_config_artifact(
                    self._experiment.experiment_id,
                    api.models.ConfigArtifact(name="GRAPHVIZ", uri=f"graphviz://{config}"),
                )

    @graphviz_config.deleter
    def graphviz_config(self) -> None:
        self._graphviz_config = None
        api.client().delete_experiment_config_artifact(self._experiment.experiment_id, "GRAPHVIZ")

    @property
    def python_config(self) -> str | None:
        return self._python_config

    @python_config.setter
    def python_config(self, config: str | None) -> None:
        self._python_config = config
        match config:
            case None:
                api.client().delete_experiment_config_artifact(
                    self._experiment.experiment_id, "PYTHON"
                )
            case str():
                api.client().insert_experiment_config_artifact(
                    self._experiment.experiment_id,
                    api.models.ConfigArtifact(name="PYTHON", uri=config),
                )

    @python_config.deleter
    def python_config(self) -> None:
        self._python_config = None
        api.client().delete_experiment_config_artifact(self._experiment.experiment_id, "PYTHON")
