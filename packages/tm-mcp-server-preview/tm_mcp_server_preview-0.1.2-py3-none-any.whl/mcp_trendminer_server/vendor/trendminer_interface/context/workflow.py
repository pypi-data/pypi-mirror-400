from trendminer_interface import _input as ip

from trendminer_interface.base import EditableBase
from trendminer_interface.constants import MAX_GET_SIZE

from .configuration_factory_base import ContextConfigurationFactoryMixin


class ContextWorkflow(EditableBase):
    """Context Workflow determining the events attachable to items of associated type

    Attributes
    ----------
    name : str
        Context workflow name
    states : list of str
        States of the workflow
    """
    endpoint = "context/workflow/"

    def __init__(self, client, identifier, name, states):

        super().__init__(client=client, identifier=identifier)
        self.name = name
        self.states = states

    def _json(self):
        return {
            "identifier": self.identifier,
            "name": self.name,
            "states": self.states,
            "startState": self.states[0],
            "endState": self.states[-1],
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<< ContextWorkflow | {self.name} >>"


class ContextWorkflowFactory(ContextConfigurationFactoryMixin):
    """Factory for creating and retrieving context workflows"""
    tm_class = ContextWorkflow

    def __call__(self, name, states, start_state=None, end_state=None):
        """Instantiate a new context workflow

        Parameters
        ----------
        name : str
            Context workflow name
        states : list of str
            Possible states of the workflow
        start_state : str, optional
            The start state; must be in `states`. Defaults to the first state in `states`.
        end_state : str, optional
            The end state; must be in `states`. Defaults to the last state in `states`.

        Returns
        -------
        ContextWorkflow
        """
        return self.tm_class(client=self.client,
                             identifier=None,
                             name=name,
                             states=states,
                             )

    def search(self, name=None):
        """Search context workflows

        Parameters
        ----------
        name : str, optional
            workflow name

        Returns
        -------
        list of ContextWorkflow
        """
        params = {"size": MAX_GET_SIZE}

        filters = []
        if name is not None:
            filters.append(f"name=='{name}'")

        if filters:
            params.update({"query": ";".join(filters)})

        content = self.client.session.paginated(keys=["content"]).get(self._endpoint, params=params)

        return [self._from_json(data) for data in content]

    def from_name(self, ref):
        """Retrieve context workflow by its name

        Parameters
        ----------
        ref : str
            workflow name

        Returns
        -------
        ContextWorkflow
        """
        return ip.object_match_nocase(self.search(name=ref), attribute="name", value=ref)

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ContextWorkflow
        """
        # make sure start and end states are in the correct order
        states = data["states"]
        start_state = data["startState"]
        end_state = data['endState']
        states = [start_state] + [state for state in states if state not in [start_state, end_state]] + [end_state]

        return self.tm_class(
            client=self.client,
            identifier=data["identifier"],
            name=data["name"],
            states=states,
        )

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_name
