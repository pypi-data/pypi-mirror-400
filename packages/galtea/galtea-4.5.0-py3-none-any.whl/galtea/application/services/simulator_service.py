"""
Simulator service for managing conversation simulation between agents and the Galtea platform.

This service orchestrates the conversation loop, calling user agents, interacting with
the conversation simulator backend, and logging the results through the platform.
"""

import logging
import warnings
from typing import Any, Dict, List, Optional

from galtea.application.services.conversation_simulator_service import ConversationSimulatorService
from galtea.application.services.inference_result_service import InferenceResultService
from galtea.application.services.session_service import SessionService
from galtea.application.services.test_case_service import TestCaseService
from galtea.application.services.trace_service import TraceService
from galtea.domain.models.generate_next_turn import GenerateNextTurnResponse
from galtea.infrastructure.clients.http_client import Client
from galtea.utils.agent import Agent, ConversationMessage
from galtea.utils.from_camel_case_base_model import FromCamelCaseBaseModel


class SimulationResult(FromCamelCaseBaseModel):
    """
    Result of a conversation simulation.

    Attributes:
        session_id (str): The session identifier
        total_turns (int): Total number of conversation turns
        messages (List[ConversationMessage]): Complete conversation history
        finished (bool): Whether the simulation finished naturally
        stopping_reason (Optional[str]): Reason for stopping if finished
        metadata (Optional[Dict[str, Any]]): Additional simulation metadata
    """

    session_id: str
    total_turns: int
    messages: List[ConversationMessage]
    finished: bool
    stopping_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SimulatorService:
    """
    Service for managing conversation simulations between agents and the Galtea platform.

    This service orchestrates the conversation loop, manages the interaction between
    user-defined agents and the conversation simulator backend, and logs all results
    through the platform's tracking system.
    """

    def __init__(
        self,
        client: Client,
        session_service: SessionService,
        test_case_service: TestCaseService,
        inference_result_service: InferenceResultService,
        conversation_simulator_service: ConversationSimulatorService,
        trace_service: TraceService,
    ):
        """Initialize the SimulatorService with required dependencies.

        Args:
            client (Client): The HTTP client for making API requests
            session_service (SessionService): Service for managing sessions
            inference_result_service (InferenceResultService): Service for logging inference results
            conversation_simulator_service (ConversationSimulatorService): Service for generating user messages
            trace_service (TraceService): Service for managing traces of tool/function calls
        """
        self.__client: Client = client
        self.__session_service: SessionService = session_service
        self.__test_case_service: TestCaseService = test_case_service
        self.__inference_result_service: InferenceResultService = inference_result_service
        self.__conversation_simulator_service: ConversationSimulatorService = conversation_simulator_service
        self.__trace_service: TraceService = trace_service
        self._logger: logging.Logger = logging.getLogger(__name__)

    def simulate(
        self,
        session_id: str,
        agent: Agent,
        max_turns: Optional[int],
        log_inference_results: Optional[bool] = None,
        enable_last_inference: bool = True,
        include_metadata: bool = False,
        agent_goes_first: bool = False,
        stop_when_agent_returns_empty_response: bool = True,
    ) -> SimulationResult:
        """
        Simulate a conversation between a user simulator and the provided agent.

        This method manages the entire conversation loop, including generating user messages,
        calling the provided agent for responses, and logging results. The version of the
        conversation simulator used is automatically captured and stored with each inference result
        for detailed analysis.

        Args:
            session_id (str): The session identifier for this conversation.
            agent (Agent): The user-defined agent that generates responses.
            max_turns (int, optional): Maximum number of conversation turns.
            log_inference_results (bool, optional): DEPRECATED - Inference results are now
                automatically tracked by the API. This parameter is kept for backward
                compatibility but no longer has any effect. Will be removed soon.
            enable_last_inference (bool, optional): If True, performs a final agent call even
                if the conversation has finished. Defaults to True.
            include_metadata (bool, optional): If True, includes additional metadata in the results.
                Defaults to False.
            agent_goes_first (bool, optional): If True, the agent will generate the first message
                before any user messages are generated. Defaults to False.
            stop_when_agent_returns_empty_response (bool, optional): If True, stops the simulation
                when the agent returns an empty response. Defaults to True.

        Returns:
            SimulationResult: An object containing the complete simulation results.

        Raises:
            ValueError: If session_id is missing or agent is None.
            Exception: If the simulation fails due to API errors or agent errors.

        Example:
            ```python
            import galtea

            # Initialize the Galtea client
            client = galtea.Galtea(api_key="your_api_key")

            # Create a session
            session = client.sessions.create(version_id="version_123")

            # Define your agent
            class MyAgent(galtea.Agent):
                def call(self, input_data: galtea.AgentInput) -> galtea.AgentResponse:
                    user_msg = input_data.last_user_message_str()
                    return galtea.AgentResponse(content=f"Response to: {user_msg}")

            # Run simulation
            result = client.simulator.simulate(
                session_id=session.id,
                agent=MyAgent(),
                max_turns=5
            )

            print(f"Simulation completed with {result.total_turns} turns")
            ```
        """
        if log_inference_results is not None:
            warnings.warn(
                (
                    "The 'log_inference_results' parameter is deprecated and will be removed soon. "
                    "Inference results are now automatically tracked by the Galtea API."
                ),
                DeprecationWarning,
                stacklevel=2,
            )

        print("Starting conversation simulation...")
        if not session_id:
            raise ValueError("Session ID is required for simulation")

        if agent is None:
            raise ValueError("Agent is required for simulation")

        if max_turns is not None and max_turns <= 0:
            raise ValueError("max_turns must be greater than 0")

        self._logger.info(f"Starting conversation simulation for session {session_id}")

        messages: List[ConversationMessage] = []
        turn_count: int = 0
        finished: bool = False
        stopping_reason: Optional[str] = None
        simulation_metadata: Dict[str, Any] = {}

        try:
            if agent_goes_first:
                # If AI goes first, call the agent to get the initial message
                self._logger.debug("AI goes first, generating initial message from agent")

                # Warn if there is an "initial prompt" in the Test Case, as it will be ignored
                session = self.__session_service.get(session_id)
                test_case = (
                    self.__test_case_service.get(session.test_case_id) if session and session.test_case_id else None
                )
                if test_case and test_case.initial_prompt and str(test_case.initial_prompt).strip():
                    self._logger.warning(
                        f"Test Case (ID: {test_case.id}) for Session (ID: {session_id}) has an initial prompt defined, "
                        "but it will be ignored because agent_goes_first is True"
                    )

                # messages array is updated with the agent response in the method
                try:
                    self.__inference_result_service._execute_agent(
                        agent,
                        session_id,
                        messages,
                        include_metadata=include_metadata,
                        # Ensure we get a response from the agent if it goes first, otherwise the API will throw error
                        throw_if_empty_agent_response=True,
                    )
                    self._logger.debug("Added initial agent message to conversation history")
                    turn_count += 1
                except ValueError:
                    self._logger.warning("Invalid agent response received, ending simulation")
                    finished = True

            # Start the conversation loop
            while not finished:
                if max_turns is not None:
                    self._logger.debug(f"Starting turn {turn_count + 1} of {max_turns}")
                else:
                    self._logger.debug(f"Starting turn {turn_count + 1}")

                # Generate user message from conversation simulator
                try:
                    user_response: GenerateNextTurnResponse = (
                        self.__conversation_simulator_service.generate_next_user_message(session_id, max_turns)
                    )
                    user_message_content: str = user_response.next_message
                    finished = user_response.finished
                    stopping_reason = user_response.stopping_reason
                    inference_result_id = user_response.inference_result_id

                    if not user_message_content and not finished:
                        self._logger.warning("Empty user message received, ending simulation")
                        break
                except Exception as e:
                    self._logger.error(f"Failed to generate user message on turn {turn_count + 1}: {e!s}")
                    raise Exception(f"Conversation simulator error: {e!s}") from e

                # Add user message to conversation history
                if user_message_content:
                    turn_count += 1
                    user_message = ConversationMessage(
                        role="user",
                        content=user_message_content,
                        metadata={"turn": turn_count, "source": "simulator"} if include_metadata else None,
                    )
                    messages.append(user_message)

                    try:
                        if not finished or enable_last_inference:
                            # Execute agent using the shared helper method
                            # messages array is updated with the agent response in the method
                            self.__inference_result_service._execute_agent(
                                agent=agent,
                                session_id=session_id,
                                messages=messages,
                                inference_result_id=inference_result_id,
                                include_metadata=include_metadata,
                                throw_if_empty_agent_response=stop_when_agent_returns_empty_response,
                            )
                    except ValueError as e:
                        self._logger.warning(f"Agent returned empty response on turn {turn_count}: {e!s}")
                        stopping_reason = f"Agent returned empty response: {e!s}"
                        break
                    except Exception as e:
                        self._logger.error(f"Agent call failed on turn {turn_count}: {e!s}")
                        stopping_reason = f"Agent error: {e!s}"
                        break

                # If conversation is finished, store the stopping reason in the session
                if finished and stopping_reason:
                    self.__session_service._update_stopping_reason(
                        session_id=session_id, stopping_reason=stopping_reason
                    )

            # Prepare simulation metadata
            if include_metadata:
                simulation_metadata = {
                    "max_turns": max_turns if max_turns is not None else "Defined by Test Case",
                    "completed_turns": turn_count,
                    "ended_naturally": finished,
                }

            self._logger.info(
                f"Simulation completed for session {session_id}: "
                f"{turn_count} turns, finished={finished}, reason={stopping_reason}"
            )

            return SimulationResult(
                session_id=session_id,
                total_turns=turn_count,
                messages=messages,
                finished=finished,
                stopping_reason=stopping_reason,
                metadata=simulation_metadata if include_metadata else None,
            )

        except Exception as e:
            self._logger.error(f"Simulation failed for session {session_id}: {e!s}")
            raise Exception(f"Simulation failed: {e!s}") from e
