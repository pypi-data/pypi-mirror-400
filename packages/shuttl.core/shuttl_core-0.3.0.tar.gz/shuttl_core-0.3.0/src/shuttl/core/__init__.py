r'''
# @shuttl-io/core

A developer-first framework for building, deploying, and managing AI agents. Stop wrestling with complex infrastructure and start shipping intelligent agents in minutes.

## Installation

**TypeScript/JavaScript:**

```bash
npm install @shuttl-io/core
# or
pnpm add @shuttl-io/core
# or
yarn add @shuttl-io/core
```

**Python:**

```bash
pip install shuttl-core
```

**Java (Maven):**

```xml
<dependency>
  <groupId>io.shuttl.module</groupId>
  <artifactId>core</artifactId>
  <version>0.1.5</version>
</dependency>
```

**Go:**

```bash
go get github.com/shuttl-io/shuttl-core-go
```

**.NET:**

```bash
dotnet add package shuttl.core
```

## Quick Start

### TypeScript

```python
import { Agent, Model, Secret, Schema } from "@shuttl-io/core";

const weatherTool = {
    name: "get_weather",
    description: "Get current weather for a location",
    schema: Schema.objectValue({
        location: Schema.stringValue("City name").isRequired(),
    }),
    execute: async (args) => {
        return { temperature: 72, condition: "sunny" };
    },
};

export const weatherAgent = new Agent({
    name: "WeatherBot",
    systemPrompt: "You help users check the weather.",
    model: Model.openAI("gpt-4", Secret.fromEnv("OPENAI_KEY")),
    tools: [weatherTool],
});
```

### Python

In Python, tools must be implemented using the `@jsii.implements()` decorator. **Do not inherit directly from the interface** - this will cause metaclass conflicts. See the [JSII Python documentation](https://aws.github.io/jsii/user-guides/lib-user/language-specific/python/#implementing-interfaces) for details.

```python
import jsii
from shuttl.core import App, StdInServer, Agent, Model, Secret
from shuttl.core.tools import ITool, ToolArg


@jsii.implements(ITool)
class WeatherTool:
    """A tool that gets weather information."""

    def __init__(self):
        self._name = "get_weather"
        self._description = "Get current weather for a location"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def execute(self, args):
        location = args.get("location", "Unknown")
        return {"temperature": 72, "condition": "sunny", "location": location}

    def produce_args(self):
        return {
            "location": ToolArg(
                name="location",
                arg_type="string",
                description="City name",
                required=True,
                default_value=None,
            ),
        }


def main():
    server = StdInServer()
    app = App("weather-bot", server)

    model = Model.open_ai("gpt-4", Secret.from_env("OPENAI_KEY"))
    agent = Agent(
        name="WeatherBot",
        system_prompt="You help users check the weather.",
        model=model,
        tools=[WeatherTool()],
    )

    app.add_agent(agent)
    app.serve()


if __name__ == "__main__":
    main()
```

Run `shuttl dev` and your agent is live.

## Core Concepts

Shuttl is built around four composable primitives:

```
┌─────────────────────────────────────────────────────────────┐
│                         TRIGGERS                            │
│   (API, Rate/Cron, Email, File, Webhook)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                          AGENT                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   System    │  │    Model    │  │   Tools & Toolkits  │ │
│  │   Prompt    │  │  (GPT, etc) │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        OUTCOMES                             │
│   (Streaming, Slack, Webhook, Custom)                       │
└─────────────────────────────────────────────────────────────┘
```

### Agents

The core unit of intelligence. An agent combines a language model with a system prompt and tools to perform tasks.

```python
export const myAgent = new Agent({
    name: "MyAgent",
    systemPrompt: "You are a helpful assistant.",
    model: Model.openAI("gpt-4", Secret.fromEnv("OPENAI_KEY")),
    tools: [],
    triggers: [],
    outcomes: [],
});
```

**Key features:**

* Multi-turn conversations with thread management
* Automatic retries with exponential backoff
* Full TypeScript support for type safety

### Tools & Toolkits

Give agents the ability to take actions: search databases, call APIs, process data, and more.

```python
const searchTool = {
    name: "search",
    description: "Search the knowledge base",
    schema: Schema.objectValue({
        query: Schema.stringValue("Search query").isRequired(),
        limit: Schema.numberValue("Max results").defaultTo(10),
    }),
    execute: async ({ query, limit }) => {
        return await searchKnowledgeBase(query, limit);
    },
};
```

Group related tools into **Toolkits** for clean, modular agent design:

```python
const weatherToolkit = new Toolkit("weather", "Tools for weather information");
weatherToolkit.addTool(getCurrentWeatherTool);
weatherToolkit.addTool(getForecastTool);
```

### Triggers

Define how and when agents are activated:

| Trigger | Description | Use Case |
|---------|-------------|----------|
| `ApiTrigger` | HTTP endpoint | Chat interfaces, webhooks |
| `Rate` | Schedule-based | Cron jobs, periodic tasks |
| `EmailTrigger` | Incoming emails | Email automation |
| `FileTrigger` | File system changes | Document processing |

```python
// Run every hour
triggers: [Rate.hours(1).bindOutcome(new StreamingOutcome())]

// Or use cron for precise scheduling
triggers: [Rate.cron("0 9 * * MON-FRI", "America/New_York")]
```

### Outcomes

Route agent responses to destinations:

| Outcome | Description | Use Case |
|---------|-------------|----------|
| `StreamingOutcome` | Real-time streaming | Chat interfaces, live feedback |
| `SlackOutcome` | Post to Slack | Notifications, reports |
| `CombinationOutcome` | Multiple destinations | Broadcast to several channels |

```python
outcomes: [
    new CombinationOutcome([
        new StreamingOutcome(),
        new SlackOutcome("#announcements"),
    ]),
]
```

### Models

Language models that power your agents. Currently supports OpenAI with more providers coming soon.

```python
// Complex analysis, important decisions
Model.openAI("gpt-4", Secret.fromEnv("KEY"))

// General purpose, good balance
Model.openAI("gpt-4o", Secret.fromEnv("KEY"))

// High volume, simple tasks
Model.openAI("gpt-4o-mini", Secret.fromEnv("KEY"))
```

**Supported providers:**

* ✅ OpenAI (GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5)
* 🚧 Anthropic (Claude 3, Claude 3.5) - Coming Soon
* 🚧 Google (Gemini Pro, Gemini Ultra) - Coming Soon
* 🚧 Local (Ollama, LM Studio) - Coming Soon

## Example: Scheduled Reporting Agent

```python
import { Agent, Model, Secret, Rate, SlackOutcome, Schema } from "@shuttl-io/core";

const reportTool = {
    name: "generate_report",
    description: "Generate a daily metrics report",
    schema: Schema.objectValue({
        date: Schema.stringValue("Report date in YYYY-MM-DD format"),
    }),
    execute: async ({ date }) => {
        return { users: 1523, revenue: 42000, churn: 0.02 };
    },
};

export const reportingAgent = new Agent({
    name: "DailyReporter",
    systemPrompt: "Generate concise daily reports. Format as bullet points.",
    model: Model.openAI("gpt-4", Secret.fromEnv("OPENAI_KEY")),
    tools: [reportTool],
    triggers: [
        Rate.cron("0 9 * * *", "America/New_York")  // 9 AM EST daily
    ],
    outcomes: [
        new SlackOutcome("#metrics-channel")
    ],
});
```

## CLI Commands

Install the Shuttl CLI:

```bash
curl -fsSL https://shuttl.dev/install.sh | bash
```

| Command | Description |
|---------|-------------|
| `shuttl dev` | Interactive development with TUI |
| `shuttl serve` | Expose agents as HTTP endpoints |
| `shuttl build` | Build your agent for deployment |

## Configuration

Create `shuttl.json` in your project root:

```json
{
    "app": "node --require ts-node/register ./src/main.ts"
}
```

## Secrets Management

Never hardcode API keys. Use the `Secret` class:

```python
// Good
model: Model.openAI("gpt-4", Secret.fromEnv("OPENAI_KEY"))

// Bad - never do this
model: Model.openAI("gpt-4", "sk-abc123...")
```

## What Can You Build?

* **Customer Support Bots** - Agents that understand context, access your knowledge base, and escalate when needed
* **Automated Workflows** - Schedule agents to process data, generate reports, or sync systems
* **Internal Tools** - AI-powered assistants that integrate with your existing stack
* **Content Pipelines** - Agents that create, review, and publish content

## License

MIT

## Links

* [Documentation](https://docs.shuttl.io)
* [GitHub](https://github.com/shuttl-io/shuttl_ai)
* [Website](https://www.shuttl.io)
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


class Agent(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Agent"):
    def __init__(
        self,
        *,
        model: "IModelFactory",
        name: builtins.str,
        system_prompt: builtins.str,
        toolkits: typing.Sequence["Toolkit"],
        outcomes: typing.Optional[typing.Sequence["IOutcome"]] = None,
        tools: typing.Optional[typing.Sequence["ITool"]] = None,
        triggers: typing.Optional[typing.Sequence["ITrigger"]] = None,
    ) -> None:
        '''
        :param model: 
        :param name: 
        :param system_prompt: 
        :param toolkits: 
        :param outcomes: 
        :param tools: 
        :param triggers: 
        '''
        props = AgentProps(
            model=model,
            name=name,
            system_prompt=system_prompt,
            toolkits=toolkits,
            outcomes=outcomes,
            tools=tools,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="getTool")
    def get_tool(self, name: builtins.str) -> "ITool":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5684bbdd0bbef8364213afb90164f887c379eb6c02b9fb4a222dc55866f49c5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ITool", jsii.invoke(self, "getTool", [name]))

    @jsii.member(jsii_name="getToolCallResult")
    def get_tool_call_result(
        self,
        call_id: builtins.str,
        result: typing.Any,
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param call_id: -
        :param result: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c357f1d52dc825b09805321f8c2577ebf97109bfc5f58c2bc8dbe6658ad8bbc2)
            check_type(argname="argument call_id", value=call_id, expected_type=type_hints["call_id"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "getToolCallResult", [call_id, result]))

    @jsii.member(jsii_name="invoke")
    def invoke(
        self,
        prompt: typing.Union[builtins.str, typing.Sequence[typing.Union[typing.Union["ModelContent", typing.Dict[builtins.str, typing.Any]], typing.Mapping[builtins.str, typing.Any]]]],
        thread_id: typing.Optional[builtins.str] = None,
        streamer: typing.Optional["IModelStreamer"] = None,
        attachments: typing.Optional[typing.Sequence[typing.Union["FileAttachment", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> "IModel":
        '''
        :param prompt: -
        :param thread_id: -
        :param streamer: -
        :param attachments: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bc8d5e10d3458b7f0128af31d93991e3603b23cf6306a2afcd6f472183b1e86)
            check_type(argname="argument prompt", value=prompt, expected_type=type_hints["prompt"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument streamer", value=streamer, expected_type=type_hints["streamer"])
            check_type(argname="argument attachments", value=attachments, expected_type=type_hints["attachments"])
        return typing.cast("IModel", jsii.ainvoke(self, "invoke", [prompt, thread_id, streamer, attachments]))

    @jsii.member(jsii_name="respondWithToolCall")
    def respond_with_tool_call(
        self,
        model_instance: "IModel",
        call_id: builtins.str,
        result: typing.Any,
        streamer: "IModelStreamer",
    ) -> None:
        '''
        :param model_instance: -
        :param call_id: -
        :param result: -
        :param streamer: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a426ad5ea12640cf63723199dd1f1999153da07b4cf299a7819e87abb23f544f)
            check_type(argname="argument model_instance", value=model_instance, expected_type=type_hints["model_instance"])
            check_type(argname="argument call_id", value=call_id, expected_type=type_hints["call_id"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            check_type(argname="argument streamer", value=streamer, expected_type=type_hints["streamer"])
        return typing.cast(None, jsii.ainvoke(self, "respondWithToolCall", [model_instance, call_id, result, streamer]))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> "IModelFactory":
        return typing.cast("IModelFactory", jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="outcomes")
    def outcomes(self) -> typing.List["IOutcome"]:
        return typing.cast(typing.List["IOutcome"], jsii.get(self, "outcomes"))

    @builtins.property
    @jsii.member(jsii_name="systemPrompt")
    def system_prompt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "systemPrompt"))

    @builtins.property
    @jsii.member(jsii_name="toolkits")
    def toolkits(self) -> typing.List["Toolkit"]:
        return typing.cast(typing.List["Toolkit"], jsii.get(self, "toolkits"))

    @builtins.property
    @jsii.member(jsii_name="tools")
    def tools(self) -> typing.List["ITool"]:
        return typing.cast(typing.List["ITool"], jsii.get(self, "tools"))

    @builtins.property
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.List["ITrigger"]:
        return typing.cast(typing.List["ITrigger"], jsii.get(self, "triggers"))


@jsii.data_type(
    jsii_type="@shuttl-io/core.AgentProps",
    jsii_struct_bases=[],
    name_mapping={
        "model": "model",
        "name": "name",
        "system_prompt": "systemPrompt",
        "toolkits": "toolkits",
        "outcomes": "outcomes",
        "tools": "tools",
        "triggers": "triggers",
    },
)
class AgentProps:
    def __init__(
        self,
        *,
        model: "IModelFactory",
        name: builtins.str,
        system_prompt: builtins.str,
        toolkits: typing.Sequence["Toolkit"],
        outcomes: typing.Optional[typing.Sequence["IOutcome"]] = None,
        tools: typing.Optional[typing.Sequence["ITool"]] = None,
        triggers: typing.Optional[typing.Sequence["ITrigger"]] = None,
    ) -> None:
        '''
        :param model: 
        :param name: 
        :param system_prompt: 
        :param toolkits: 
        :param outcomes: 
        :param tools: 
        :param triggers: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__772e09ef2798d90b831b5cd341522046082132dc43579d76188b9ddd9e90a3d7)
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument system_prompt", value=system_prompt, expected_type=type_hints["system_prompt"])
            check_type(argname="argument toolkits", value=toolkits, expected_type=type_hints["toolkits"])
            check_type(argname="argument outcomes", value=outcomes, expected_type=type_hints["outcomes"])
            check_type(argname="argument tools", value=tools, expected_type=type_hints["tools"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "model": model,
            "name": name,
            "system_prompt": system_prompt,
            "toolkits": toolkits,
        }
        if outcomes is not None:
            self._values["outcomes"] = outcomes
        if tools is not None:
            self._values["tools"] = tools
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def model(self) -> "IModelFactory":
        result = self._values.get("model")
        assert result is not None, "Required property 'model' is missing"
        return typing.cast("IModelFactory", result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def system_prompt(self) -> builtins.str:
        result = self._values.get("system_prompt")
        assert result is not None, "Required property 'system_prompt' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def toolkits(self) -> typing.List["Toolkit"]:
        result = self._values.get("toolkits")
        assert result is not None, "Required property 'toolkits' is missing"
        return typing.cast(typing.List["Toolkit"], result)

    @builtins.property
    def outcomes(self) -> typing.Optional[typing.List["IOutcome"]]:
        result = self._values.get("outcomes")
        return typing.cast(typing.Optional[typing.List["IOutcome"]], result)

    @builtins.property
    def tools(self) -> typing.Optional[typing.List["ITool"]]:
        result = self._values.get("tools")
        return typing.cast(typing.Optional[typing.List["ITool"]], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.List["ITrigger"]]:
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.List["ITrigger"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AgentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ApiAuth",
    jsii_struct_bases=[],
    name_mapping={"auth_type": "authType", "value": "value"},
)
class ApiAuth:
    def __init__(self, *, auth_type: builtins.str, value: builtins.str) -> None:
        '''
        :param auth_type: 
        :param value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e802366751dd7472ced51de248ecdc5d45fcc2095126a20b69b505a251b5663)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_type": auth_type,
            "value": value,
        }

    @builtins.property
    def auth_type(self) -> builtins.str:
        result = self._values.get("auth_type")
        assert result is not None, "Required property 'auth_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ApiTriggerArgs",
    jsii_struct_bases=[],
    name_mapping={
        "host_name": "hostName",
        "method": "method",
        "auth": "auth",
        "body": "body",
        "cookies": "cookies",
        "headers": "headers",
        "path_params": "pathParams",
        "query_params": "queryParams",
    },
)
class ApiTriggerArgs:
    def __init__(
        self,
        *,
        host_name: builtins.str,
        method: builtins.str,
        auth: typing.Optional[typing.Union[ApiAuth, typing.Dict[builtins.str, typing.Any]]] = None,
        body: typing.Any = None,
        cookies: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        path_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        query_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param host_name: 
        :param method: 
        :param auth: 
        :param body: 
        :param cookies: 
        :param headers: 
        :param path_params: 
        :param query_params: 
        '''
        if isinstance(auth, dict):
            auth = ApiAuth(**auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed9cbe1300a30dc34c2bb84fa4e0ca9f5b14d80762e1f50699d6979dfd1ead0)
            check_type(argname="argument host_name", value=host_name, expected_type=type_hints["host_name"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument cookies", value=cookies, expected_type=type_hints["cookies"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument path_params", value=path_params, expected_type=type_hints["path_params"])
            check_type(argname="argument query_params", value=query_params, expected_type=type_hints["query_params"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host_name": host_name,
            "method": method,
        }
        if auth is not None:
            self._values["auth"] = auth
        if body is not None:
            self._values["body"] = body
        if cookies is not None:
            self._values["cookies"] = cookies
        if headers is not None:
            self._values["headers"] = headers
        if path_params is not None:
            self._values["path_params"] = path_params
        if query_params is not None:
            self._values["query_params"] = query_params

    @builtins.property
    def host_name(self) -> builtins.str:
        result = self._values.get("host_name")
        assert result is not None, "Required property 'host_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> builtins.str:
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth(self) -> typing.Optional[ApiAuth]:
        result = self._values.get("auth")
        return typing.cast(typing.Optional[ApiAuth], result)

    @builtins.property
    def body(self) -> typing.Any:
        result = self._values.get("body")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cookies(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("cookies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def path_params(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("path_params")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def query_params(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("query_params")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiTriggerArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ApiTriggerConfig",
    jsii_struct_bases=[],
    name_mapping={"authenticator": "authenticator", "cors": "cors"},
)
class ApiTriggerConfig:
    def __init__(
        self,
        *,
        authenticator: typing.Optional["IApiAuthenticator"] = None,
        cors: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param authenticator: 
        :param cors: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f4f099b44cc988eb7dbbe99a2ebb3e4b4bdb5f969533a1172f12bd926d2872)
            check_type(argname="argument authenticator", value=authenticator, expected_type=type_hints["authenticator"])
            check_type(argname="argument cors", value=cors, expected_type=type_hints["cors"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authenticator is not None:
            self._values["authenticator"] = authenticator
        if cors is not None:
            self._values["cors"] = cors

    @builtins.property
    def authenticator(self) -> typing.Optional["IApiAuthenticator"]:
        result = self._values.get("authenticator")
        return typing.cast(typing.Optional["IApiAuthenticator"], result)

    @builtins.property
    def cors(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("cors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiTriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class App(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.App"):
    def __init__(self, name: builtins.str, server: "IServer") -> None:
        '''
        :param name: -
        :param server: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43533246dc785273087a131e3882a92eecb170c828986e171d107be193116a40)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument server", value=server, expected_type=type_hints["server"])
        jsii.create(self.__class__, self, [name, server])

    @jsii.member(jsii_name="addAgent")
    def add_agent(self, agent: Agent) -> None:
        '''
        :param agent: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01984d81fd457408a23c7e84fee151b085ed90597fd46465a123b5f1b19e1acf)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
        return typing.cast(None, jsii.invoke(self, "addAgent", [agent]))

    @jsii.member(jsii_name="addToolkit")
    def add_toolkit(self, toolkit: "Toolkit") -> None:
        '''
        :param toolkit: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e1cd21702140418dddee57370c5464866f4bc61178c6ba157d0d0e06390222c)
            check_type(argname="argument toolkit", value=toolkit, expected_type=type_hints["toolkit"])
        return typing.cast(None, jsii.invoke(self, "addToolkit", [toolkit]))

    @jsii.member(jsii_name="serve")
    def serve(self) -> None:
        return typing.cast(None, jsii.ainvoke(self, "serve", []))

    @builtins.property
    @jsii.member(jsii_name="agents")
    def agents(self) -> typing.List[Agent]:
        return typing.cast(typing.List[Agent], jsii.get(self, "agents"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="server")
    def server(self) -> "IServer":
        return typing.cast("IServer", jsii.get(self, "server"))


@jsii.data_type(
    jsii_type="@shuttl-io/core.EmailTriggerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "folder": "folder",
        "from_address": "fromAddress",
        "inbox_name": "inboxName",
        "subject_pattern": "subjectPattern",
    },
)
class EmailTriggerConfig:
    def __init__(
        self,
        *,
        domain: builtins.str,
        folder: builtins.str,
        from_address: builtins.str,
        inbox_name: builtins.str,
        subject_pattern: builtins.str,
    ) -> None:
        '''
        :param domain: 
        :param folder: 
        :param from_address: 
        :param inbox_name: 
        :param subject_pattern: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2a98b590bd52775dda41ea08af1f5c079e64d60814426456f202c906a70db2)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument from_address", value=from_address, expected_type=type_hints["from_address"])
            check_type(argname="argument inbox_name", value=inbox_name, expected_type=type_hints["inbox_name"])
            check_type(argname="argument subject_pattern", value=subject_pattern, expected_type=type_hints["subject_pattern"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "folder": folder,
            "from_address": from_address,
            "inbox_name": inbox_name,
            "subject_pattern": subject_pattern,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def folder(self) -> builtins.str:
        result = self._values.get("folder")
        assert result is not None, "Required property 'folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def from_address(self) -> builtins.str:
        result = self._values.get("from_address")
        assert result is not None, "Required property 'from_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inbox_name(self) -> builtins.str:
        result = self._values.get("inbox_name")
        assert result is not None, "Required property 'inbox_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject_pattern(self) -> builtins.str:
        result = self._values.get("subject_pattern")
        assert result is not None, "Required property 'subject_pattern' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailTriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.FileAttachment",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "name": "name",
        "mime_type": "mimeType",
        "path": "path",
    },
)
class FileAttachment:
    def __init__(
        self,
        *,
        content: builtins.str,
        name: builtins.str,
        mime_type: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents a file attachment sent with a chat message.

        :param content: Base64 encoded file content.
        :param name: The file name.
        :param mime_type: MIME type of the file.
        :param path: The file path (optional, may not be relevant in all contexts).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4b87a01c828afa7d42dfa3adc5e53bbd3d07b84a17f5d3e4b84c1f727f075bd)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument mime_type", value=mime_type, expected_type=type_hints["mime_type"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "name": name,
        }
        if mime_type is not None:
            self._values["mime_type"] = mime_type
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def content(self) -> builtins.str:
        '''Base64 encoded file content.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The file name.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mime_type(self) -> typing.Optional[builtins.str]:
        '''MIME type of the file.'''
        result = self._values.get("mime_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The file path (optional, may not be relevant in all contexts).'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileAttachment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.FileTriggerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_extensions": "allowedExtensions",
        "max_file_size": "maxFileSize",
        "s3_bucket": "s3Bucket",
        "upload_path": "uploadPath",
    },
)
class FileTriggerConfig:
    def __init__(
        self,
        *,
        allowed_extensions: typing.Sequence[builtins.str],
        max_file_size: jsii.Number,
        s3_bucket: builtins.str,
        upload_path: builtins.str,
    ) -> None:
        '''
        :param allowed_extensions: 
        :param max_file_size: 
        :param s3_bucket: 
        :param upload_path: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca8007b7d694698dff28eaa147f22cfb1a74b3acd1ed88eea72bb85c856a88e4)
            check_type(argname="argument allowed_extensions", value=allowed_extensions, expected_type=type_hints["allowed_extensions"])
            check_type(argname="argument max_file_size", value=max_file_size, expected_type=type_hints["max_file_size"])
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument upload_path", value=upload_path, expected_type=type_hints["upload_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allowed_extensions": allowed_extensions,
            "max_file_size": max_file_size,
            "s3_bucket": s3_bucket,
            "upload_path": upload_path,
        }

    @builtins.property
    def allowed_extensions(self) -> typing.List[builtins.str]:
        result = self._values.get("allowed_extensions")
        assert result is not None, "Required property 'allowed_extensions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def max_file_size(self) -> jsii.Number:
        result = self._values.get("max_file_size")
        assert result is not None, "Required property 'max_file_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def s3_bucket(self) -> builtins.str:
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def upload_path(self) -> builtins.str:
        result = self._values.get("upload_path")
        assert result is not None, "Required property 'upload_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileTriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@shuttl-io/core.IAgentStreamerWriter")
class IAgentStreamerWriter(typing_extensions.Protocol):
    @jsii.member(jsii_name="write")
    def write(self, value: builtins.str) -> None:
        '''
        :param value: -
        '''
        ...

    @jsii.member(jsii_name="writeObject")
    def write_object(self, value: typing.Any) -> None:
        '''
        :param value: -
        '''
        ...


class _IAgentStreamerWriterProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IAgentStreamerWriter"

    @jsii.member(jsii_name="write")
    def write(self, value: builtins.str) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d789e8211b96d69d0d9dc11552926a41d95d137bd4c834683889acdf03d85853)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "write", [value]))

    @jsii.member(jsii_name="writeObject")
    def write_object(self, value: typing.Any) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf7804ae8cd0b2e0bd19aefffc531c49792898e187bcffec35172beddbea7ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "writeObject", [value]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentStreamerWriter).__jsii_proxy_class__ = lambda : _IAgentStreamerWriterProxy


@jsii.interface(jsii_type="@shuttl-io/core.IApiAuthenticator")
class IApiAuthenticator(typing_extensions.Protocol):
    @jsii.member(jsii_name="authenticate")
    def authenticate(
        self,
        *,
        host_name: builtins.str,
        method: builtins.str,
        auth: typing.Optional[typing.Union[ApiAuth, typing.Dict[builtins.str, typing.Any]]] = None,
        body: typing.Any = None,
        cookies: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        path_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        query_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> builtins.bool:
        '''
        :param host_name: 
        :param method: 
        :param auth: 
        :param body: 
        :param cookies: 
        :param headers: 
        :param path_params: 
        :param query_params: 
        '''
        ...


class _IApiAuthenticatorProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IApiAuthenticator"

    @jsii.member(jsii_name="authenticate")
    def authenticate(
        self,
        *,
        host_name: builtins.str,
        method: builtins.str,
        auth: typing.Optional[typing.Union[ApiAuth, typing.Dict[builtins.str, typing.Any]]] = None,
        body: typing.Any = None,
        cookies: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        path_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        query_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> builtins.bool:
        '''
        :param host_name: 
        :param method: 
        :param auth: 
        :param body: 
        :param cookies: 
        :param headers: 
        :param path_params: 
        :param query_params: 
        '''
        args = ApiTriggerArgs(
            host_name=host_name,
            method=method,
            auth=auth,
            body=body,
            cookies=cookies,
            headers=headers,
            path_params=path_params,
            query_params=query_params,
        )

        return typing.cast(builtins.bool, jsii.invoke(self, "authenticate", [args]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApiAuthenticator).__jsii_proxy_class__ = lambda : _IApiAuthenticatorProxy


@jsii.interface(jsii_type="@shuttl-io/core.IModel")
class IModel(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="threadId")
    def thread_id(self) -> typing.Optional[builtins.str]:
        ...

    @jsii.member(jsii_name="invoke")
    def invoke(
        self,
        prompt: typing.Sequence[typing.Union[typing.Union["ModelContent", typing.Dict[builtins.str, typing.Any]], typing.Mapping[builtins.str, typing.Any]]],
        streamer: "IModelStreamer",
    ) -> None:
        '''
        :param prompt: -
        :param streamer: -
        '''
        ...


class _IModelProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IModel"

    @builtins.property
    @jsii.member(jsii_name="threadId")
    def thread_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threadId"))

    @jsii.member(jsii_name="invoke")
    def invoke(
        self,
        prompt: typing.Sequence[typing.Union[typing.Union["ModelContent", typing.Dict[builtins.str, typing.Any]], typing.Mapping[builtins.str, typing.Any]]],
        streamer: "IModelStreamer",
    ) -> None:
        '''
        :param prompt: -
        :param streamer: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc0405cb1c62c8c0f09fc66cc0baf65b1eb2a40772e4d1c3c18c375e177ae81)
            check_type(argname="argument prompt", value=prompt, expected_type=type_hints["prompt"])
            check_type(argname="argument streamer", value=streamer, expected_type=type_hints["streamer"])
        return typing.cast(None, jsii.invoke(self, "invoke", [prompt, streamer]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModel).__jsii_proxy_class__ = lambda : _IModelProxy


@jsii.interface(jsii_type="@shuttl-io/core.IModelFactory")
class IModelFactory(typing_extensions.Protocol):
    @jsii.member(jsii_name="create")
    def create(self, props: "IModelFactoryProps") -> IModel:
        '''
        :param props: -
        '''
        ...


class _IModelFactoryProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IModelFactory"

    @jsii.member(jsii_name="create")
    def create(self, props: "IModelFactoryProps") -> IModel:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a43295bce67af72272e842a02d29a142058c39c0e1ffab0ea8278f4bdf090fd)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(IModel, jsii.invoke(self, "create", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModelFactory).__jsii_proxy_class__ = lambda : _IModelFactoryProxy


@jsii.interface(jsii_type="@shuttl-io/core.IModelFactoryProps")
class IModelFactoryProps(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="systemPrompt")
    def system_prompt(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        ...

    @builtins.property
    @jsii.member(jsii_name="tools")
    def tools(self) -> typing.Optional[typing.List["ITool"]]:
        ...


class _IModelFactoryPropsProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IModelFactoryProps"

    @builtins.property
    @jsii.member(jsii_name="systemPrompt")
    def system_prompt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "systemPrompt"))

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "configuration"))

    @builtins.property
    @jsii.member(jsii_name="tools")
    def tools(self) -> typing.Optional[typing.List["ITool"]]:
        return typing.cast(typing.Optional[typing.List["ITool"]], jsii.get(self, "tools"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModelFactoryProps).__jsii_proxy_class__ = lambda : _IModelFactoryPropsProxy


@jsii.interface(jsii_type="@shuttl-io/core.IModelResponseStream")
class IModelResponseStream(typing_extensions.Protocol):
    @jsii.member(jsii_name="next")
    def next(self) -> "ModelResponseStreamValue":
        ...


class _IModelResponseStreamProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IModelResponseStream"

    @jsii.member(jsii_name="next")
    def next(self) -> "ModelResponseStreamValue":
        return typing.cast("ModelResponseStreamValue", jsii.invoke(self, "next", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModelResponseStream).__jsii_proxy_class__ = lambda : _IModelResponseStreamProxy


@jsii.interface(jsii_type="@shuttl-io/core.IModelStreamer")
class IModelStreamer(typing_extensions.Protocol):
    @jsii.member(jsii_name="recieve")
    def recieve(
        self,
        model: IModel,
        *,
        data: typing.Union[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]]]],
        event_name: builtins.str,
        model_instance: typing.Optional[IModel] = None,
        thread_id: typing.Optional[builtins.str] = None,
        usage: typing.Optional[typing.Union["Usage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param model: -
        :param data: 
        :param event_name: 
        :param model_instance: 
        :param thread_id: 
        :param usage: 
        '''
        ...


class _IModelStreamerProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IModelStreamer"

    @jsii.member(jsii_name="recieve")
    def recieve(
        self,
        model: IModel,
        *,
        data: typing.Union[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]]]],
        event_name: builtins.str,
        model_instance: typing.Optional[IModel] = None,
        thread_id: typing.Optional[builtins.str] = None,
        usage: typing.Optional[typing.Union["Usage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param model: -
        :param data: 
        :param event_name: 
        :param model_instance: 
        :param thread_id: 
        :param usage: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f653d3d9c6c4d52acd8e641a6063e4a96b1a83995e001c2dd0e736cbe04634)
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
        content = ModelResponse(
            data=data,
            event_name=event_name,
            model_instance=model_instance,
            thread_id=thread_id,
            usage=usage,
        )

        return typing.cast(None, jsii.invoke(self, "recieve", [model, content]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModelStreamer).__jsii_proxy_class__ = lambda : _IModelStreamerProxy


@jsii.interface(jsii_type="@shuttl-io/core.IOutcome")
class IOutcome(typing_extensions.Protocol):
    @jsii.member(jsii_name="bindToRequest")
    def bind_to_request(self, request: typing.Any) -> None:
        '''
        :param request: -
        '''
        ...

    @jsii.member(jsii_name="send")
    def send(self, message_stream: IModelResponseStream) -> None:
        '''
        :param message_stream: -
        '''
        ...


class _IOutcomeProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IOutcome"

    @jsii.member(jsii_name="bindToRequest")
    def bind_to_request(self, request: typing.Any) -> None:
        '''
        :param request: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd6fa69a7f3da5347340534c57cb92847212c71d6f93a48fee96d4f6c7ed87a9)
            check_type(argname="argument request", value=request, expected_type=type_hints["request"])
        return typing.cast(None, jsii.invoke(self, "bindToRequest", [request]))

    @jsii.member(jsii_name="send")
    def send(self, message_stream: IModelResponseStream) -> None:
        '''
        :param message_stream: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3263f190d40f408b6178f98150ba715a3618f0465d82a7ef428faa664c1b8946)
            check_type(argname="argument message_stream", value=message_stream, expected_type=type_hints["message_stream"])
        return typing.cast(None, jsii.invoke(self, "send", [message_stream]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOutcome).__jsii_proxy_class__ = lambda : _IOutcomeProxy


@jsii.interface(jsii_type="@shuttl-io/core.IPCRequest")
class IPCRequest(typing_extensions.Protocol):
    '''Request message format from the host CLI.'''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique request ID for correlation.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        '''The method/action to invoke.'''
        ...

    @method.setter
    def method(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="body")
    def body(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Optional parameters for the method.'''
        ...

    @body.setter
    def body(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        ...


class _IPCRequestProxy:
    '''Request message format from the host CLI.'''

    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IPCRequest"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique request ID for correlation.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f47c4d6cf2f6618519902c3e7e8b5ca200c6ea27ef967ef81d537c2d601a4555)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        '''The method/action to invoke.'''
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cac852b8ecd970646faefd7e7f5c78bf83418bddc535730146d6ba9907fc3ac1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="body")
    def body(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Optional parameters for the method.'''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "body"))

    @body.setter
    def body(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e00a6ed70830df398a313352c3aa734cc960a79eb64283053ae0ce2fb885b37e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "body", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPCRequest).__jsii_proxy_class__ = lambda : _IPCRequestProxy


@jsii.interface(jsii_type="@shuttl-io/core.IPCResponse")
class IPCResponse(typing_extensions.Protocol):
    '''Response message format sent back to the host CLI.'''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Correlates to the request ID.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="success")
    def success(self) -> builtins.bool:
        '''Whether the request was successful.'''
        ...

    @success.setter
    def success(self, value: builtins.bool) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="errorObj")
    def error_obj(self) -> typing.Optional["IPCResponseError"]:
        '''Error information (on failure).'''
        ...

    @error_obj.setter
    def error_obj(self, value: typing.Optional["IPCResponseError"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> typing.Any:
        '''The result data (on success).'''
        ...

    @result.setter
    def result(self, value: typing.Any) -> None:
        ...


class _IPCResponseProxy:
    '''Response message format sent back to the host CLI.'''

    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IPCResponse"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Correlates to the request ID.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0bfe00123d03338d92367cb4a0c215e5e30087f33a0f639f19b791714d9624d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="success")
    def success(self) -> builtins.bool:
        '''Whether the request was successful.'''
        return typing.cast(builtins.bool, jsii.get(self, "success"))

    @success.setter
    def success(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad26ac74919683bd213b6b7c419f9948aa9bc38477559c6c6ae0932b7977265)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "success", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="errorObj")
    def error_obj(self) -> typing.Optional["IPCResponseError"]:
        '''Error information (on failure).'''
        return typing.cast(typing.Optional["IPCResponseError"], jsii.get(self, "errorObj"))

    @error_obj.setter
    def error_obj(self, value: typing.Optional["IPCResponseError"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47cf3fdcbe5ccb300d3cbb6a771bc0d5a9a492eff13540af498af7dc51af0c6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorObj", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> typing.Any:
        '''The result data (on success).'''
        return typing.cast(typing.Any, jsii.get(self, "result"))

    @result.setter
    def result(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6cfccd993dda54e23963d06288649b6b8b95821a2fff400545a0d111c8dade4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "result", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPCResponse).__jsii_proxy_class__ = lambda : _IPCResponseProxy


@jsii.interface(jsii_type="@shuttl-io/core.IPCResponseError")
class IPCResponseError(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="code")
    def code(self) -> builtins.str:
        ...

    @code.setter
    def code(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        ...

    @message.setter
    def message(self, value: builtins.str) -> None:
        ...


class _IPCResponseErrorProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IPCResponseError"

    @builtins.property
    @jsii.member(jsii_name="code")
    def code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "code"))

    @code.setter
    def code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6904c04f031971514c42cb890a6158dfc42dec3778e4da2b66abdad6d6320137)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "code", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="message")
    def message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "message"))

    @message.setter
    def message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e8d00f9cd00687ab975ee8a12462f4808c9da7b9777f99683079ffb1e5520e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "message", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPCResponseError).__jsii_proxy_class__ = lambda : _IPCResponseErrorProxy


@jsii.interface(jsii_type="@shuttl-io/core.IRateTriggerOnTrigger")
class IRateTriggerOnTrigger(typing_extensions.Protocol):
    @jsii.member(jsii_name="onTrigger")
    def on_trigger(self) -> typing.List["InputContent"]:
        ...


class _IRateTriggerOnTriggerProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IRateTriggerOnTrigger"

    @jsii.member(jsii_name="onTrigger")
    def on_trigger(self) -> typing.List["InputContent"]:
        return typing.cast(typing.List["InputContent"], jsii.invoke(self, "onTrigger", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRateTriggerOnTrigger).__jsii_proxy_class__ = lambda : _IRateTriggerOnTriggerProxy


@jsii.interface(jsii_type="@shuttl-io/core.ISecret")
class ISecret(typing_extensions.Protocol):
    @jsii.member(jsii_name="resolveSecret")
    def resolve_secret(self) -> builtins.str:
        ...


class _ISecretProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.ISecret"

    @jsii.member(jsii_name="resolveSecret")
    def resolve_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "resolveSecret", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecret).__jsii_proxy_class__ = lambda : _ISecretProxy


@jsii.interface(jsii_type="@shuttl-io/core.IServer")
class IServer(typing_extensions.Protocol):
    @jsii.member(jsii_name="accept")
    def accept(self, app: typing.Any) -> None:
        '''
        :param app: -
        '''
        ...

    @jsii.member(jsii_name="start")
    def start(self) -> None:
        ...

    @jsii.member(jsii_name="stop")
    def stop(self) -> None:
        ...


class _IServerProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.IServer"

    @jsii.member(jsii_name="accept")
    def accept(self, app: typing.Any) -> None:
        '''
        :param app: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6dcdb264b720904f8fcd9fa433897ef3b2ca24edd5612f05268cb41df17833)
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
        return typing.cast(None, jsii.invoke(self, "accept", [app]))

    @jsii.member(jsii_name="start")
    def start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "start", []))

    @jsii.member(jsii_name="stop")
    def stop(self) -> None:
        return typing.cast(None, jsii.invoke(self, "stop", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServer).__jsii_proxy_class__ = lambda : _IServerProxy


@jsii.interface(jsii_type="@shuttl-io/core.ITool")
class ITool(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.Optional["Schema"]:
        ...

    @schema.setter
    def schema(self, value: typing.Optional["Schema"]) -> None:
        ...

    @jsii.member(jsii_name="execute")
    def execute(self, args: typing.Mapping[builtins.str, typing.Any]) -> typing.Any:
        '''
        :param args: -
        '''
        ...


class _IToolProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.ITool"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0fd3df91c05e2ff5ab390508306dffbd9f94bc1e370ff9134842fdbe44a251c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9610a90c39cdba00baca8ad2e5bad6527eb3fb1d55f7275ea2498ee8d94e0b37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> typing.Optional["Schema"]:
        return typing.cast(typing.Optional["Schema"], jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: typing.Optional["Schema"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde4713b77352fa4457cb7fd334b8916978091173e4a083f528dcf1e511383c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="execute")
    def execute(self, args: typing.Mapping[builtins.str, typing.Any]) -> typing.Any:
        '''
        :param args: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dae74019e2dcc67378db8e450efc9f233b8147c930b4aedb717cb16bc7149529)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        return typing.cast(typing.Any, jsii.invoke(self, "execute", [args]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITool).__jsii_proxy_class__ = lambda : _IToolProxy


@jsii.interface(jsii_type="@shuttl-io/core.ITrigger")
class ITrigger(typing_extensions.Protocol):
    '''Represents a trigger that can activate an agent.

    Triggers can take any arguments and then return what the input should be for the agent.
    Triggers also can validate the arguments and return an error if the arguments are invalid.
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The unique name of this trigger instance.

        If not set, defaults to triggerType.
        '''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="triggerConfig")
    def trigger_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The configuration for the trigger.'''
        ...

    @trigger_config.setter
    def trigger_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        ...

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        ...

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        ...

    @jsii.member(jsii_name="activate")
    def activate(self, args: typing.Any, invoker: "ITriggerInvoker") -> None:
        '''Activates the trigger and returns the input for the agent.

        :param args: - The arguments for the trigger.
        :param invoker: -

        :return: The input for the agent.
        '''
        ...

    @jsii.member(jsii_name="bindOutcome")
    def bind_outcome(self, outcome: IOutcome) -> "ITrigger":
        '''binds the outcome to the trigger.

        :param outcome: - The outcome to bind to the trigger.

        :return: The bound outcome.
        '''
        ...

    @jsii.member(jsii_name="validate")
    def validate(self, args: typing.Any) -> typing.Mapping[builtins.str, typing.Any]:
        '''Validates the arguments for the trigger.

        :param args: - The arguments for the trigger.

        :return: The validation result.
        '''
        ...

    @jsii.member(jsii_name="withName")
    def with_name(self, name: builtins.str) -> "ITrigger":
        '''Sets the name of the trigger.

        :param name: - The name to set for the trigger.

        :return: The trigger instance for chaining
        '''
        ...


class _ITriggerProxy:
    '''Represents a trigger that can activate an agent.

    Triggers can take any arguments and then return what the input should be for the agent.
    Triggers also can validate the arguments and return an error if the arguments are invalid.
    '''

    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.ITrigger"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The unique name of this trigger instance.

        If not set, defaults to triggerType.
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3134ba045df9b7dd31dee64bd2afc90d2df728641cf5eb61391f1ee3289e65b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerConfig")
    def trigger_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The configuration for the trigger.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "triggerConfig"))

    @trigger_config.setter
    def trigger_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d938f80efbeee3b03d22a9d42ea409abc1f9afc91d4a4d4188ed2df32aa1d726)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc57da97f01cb79ce3dbafffc17d8568b2fd74712c6149b60f108707f08d7f68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff37f4f04c9c5488623679f2262e1f67a7cc0a4c61c541b3207799db51bbba24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="activate")
    def activate(self, args: typing.Any, invoker: "ITriggerInvoker") -> None:
        '''Activates the trigger and returns the input for the agent.

        :param args: - The arguments for the trigger.
        :param invoker: -

        :return: The input for the agent.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c8e7f74423e73a60bef544b22cff2196848b539fea2c0780ca8b1948f35e099)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
            check_type(argname="argument invoker", value=invoker, expected_type=type_hints["invoker"])
        return typing.cast(None, jsii.invoke(self, "activate", [args, invoker]))

    @jsii.member(jsii_name="bindOutcome")
    def bind_outcome(self, outcome: IOutcome) -> ITrigger:
        '''binds the outcome to the trigger.

        :param outcome: - The outcome to bind to the trigger.

        :return: The bound outcome.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb45739514651aaeafcd9ae6e456d9e2eb7b1925a7a885e80598bf52fb4fc77)
            check_type(argname="argument outcome", value=outcome, expected_type=type_hints["outcome"])
        return typing.cast(ITrigger, jsii.invoke(self, "bindOutcome", [outcome]))

    @jsii.member(jsii_name="validate")
    def validate(self, args: typing.Any) -> typing.Mapping[builtins.str, typing.Any]:
        '''Validates the arguments for the trigger.

        :param args: - The arguments for the trigger.

        :return: The validation result.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2edbb9866ea0992dac34bbaad4ef3ea74acd211e8e7a1b129ca2abc7b5f072b)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "validate", [args]))

    @jsii.member(jsii_name="withName")
    def with_name(self, name: builtins.str) -> ITrigger:
        '''Sets the name of the trigger.

        :param name: - The name to set for the trigger.

        :return: The trigger instance for chaining
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e2ff7e76bf4f56a2212ad1e2f2468cad3086373ed9420564964da6369b7ecb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(ITrigger, jsii.invoke(self, "withName", [name]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITrigger).__jsii_proxy_class__ = lambda : _ITriggerProxy


@jsii.interface(jsii_type="@shuttl-io/core.ITriggerInvoker")
class ITriggerInvoker(typing_extensions.Protocol):
    @jsii.member(jsii_name="defaultOutcome")
    def default_outcome(self, stream: IModelResponseStream) -> None:
        '''
        :param stream: -
        '''
        ...

    @jsii.member(jsii_name="invoke")
    def invoke(
        self,
        prompt: typing.Sequence[typing.Union["InputContent", typing.Dict[builtins.str, typing.Any]]],
    ) -> IModelResponseStream:
        '''
        :param prompt: -
        '''
        ...


class _ITriggerInvokerProxy:
    __jsii_type__: typing.ClassVar[str] = "@shuttl-io/core.ITriggerInvoker"

    @jsii.member(jsii_name="defaultOutcome")
    def default_outcome(self, stream: IModelResponseStream) -> None:
        '''
        :param stream: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__218f8469c3be1d700c0181c0a20bd6c0ccdf6282e69926295a2a1ffcea919fdb)
            check_type(argname="argument stream", value=stream, expected_type=type_hints["stream"])
        return typing.cast(None, jsii.invoke(self, "defaultOutcome", [stream]))

    @jsii.member(jsii_name="invoke")
    def invoke(
        self,
        prompt: typing.Sequence[typing.Union["InputContent", typing.Dict[builtins.str, typing.Any]]],
    ) -> IModelResponseStream:
        '''
        :param prompt: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf7bdb8585658c1c746590c8cefebf138f2edc15ed6003d9f4a9c8a9614aacef)
            check_type(argname="argument prompt", value=prompt, expected_type=type_hints["prompt"])
        return typing.cast(IModelResponseStream, jsii.invoke(self, "invoke", [prompt]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITriggerInvoker).__jsii_proxy_class__ = lambda : _ITriggerInvokerProxy


@jsii.data_type(
    jsii_type="@shuttl-io/core.InputContent",
    jsii_struct_bases=[],
    name_mapping={
        "type_name": "typeName",
        "file": "file",
        "file_data": "fileData",
        "image": "image",
        "text": "text",
    },
)
class InputContent:
    def __init__(
        self,
        *,
        type_name: builtins.str,
        file: typing.Optional[builtins.str] = None,
        file_data: typing.Optional[typing.Union[FileAttachment, typing.Dict[builtins.str, typing.Any]]] = None,
        image: typing.Optional[builtins.str] = None,
        text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type_name: 
        :param file: 
        :param file_data: For file type, can include base64 content.
        :param image: 
        :param text: 
        '''
        if isinstance(file_data, dict):
            file_data = FileAttachment(**file_data)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce6e38eb3d3c5892fc5c36ee215dee558abe274965a9053f11181e438aa84a64)
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
            check_type(argname="argument file_data", value=file_data, expected_type=type_hints["file_data"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type_name": type_name,
        }
        if file is not None:
            self._values["file"] = file
        if file_data is not None:
            self._values["file_data"] = file_data
        if image is not None:
            self._values["image"] = image
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def type_name(self) -> builtins.str:
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_data(self) -> typing.Optional[FileAttachment]:
        '''For file type, can include base64 content.'''
        result = self._values.get("file_data")
        return typing.cast(typing.Optional[FileAttachment], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def text(self) -> typing.Optional[builtins.str]:
        result = self._values.get("text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputContent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.InputTokensDetails",
    jsii_struct_bases=[],
    name_mapping={"cached_tokens": "cachedTokens"},
)
class InputTokensDetails:
    def __init__(self, *, cached_tokens: jsii.Number) -> None:
        '''
        :param cached_tokens: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c37db4d50d0702158938c6db914cbd3af7ae1d5002a4c02c2627e14ba07e725)
            check_type(argname="argument cached_tokens", value=cached_tokens, expected_type=type_hints["cached_tokens"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cached_tokens": cached_tokens,
        }

    @builtins.property
    def cached_tokens(self) -> jsii.Number:
        result = self._values.get("cached_tokens")
        assert result is not None, "Required property 'cached_tokens' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputTokensDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Model(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Model"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="openAI")
    @builtins.classmethod
    def open_ai(
        cls,
        identifier: builtins.str,
        api_key: ISecret,
        configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> IModelFactory:
        '''
        :param identifier: -
        :param api_key: -
        :param configuration: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__657743938d459287068308a40aad8943bac32cdbfe386c556d1939e937695a63)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        return typing.cast(IModelFactory, jsii.sinvoke(cls, "openAI", [identifier, api_key, configuration]))


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelContent",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "role": "role"},
)
class ModelContent:
    def __init__(
        self,
        *,
        content: typing.Union[builtins.str, typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]]]],
        role: builtins.str,
    ) -> None:
        '''
        :param content: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b30701319b1c0c5c1c04ccf40e9586ba0cbaa596c04bdca1a59b9e2963f86535)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "role": role,
        }

    @builtins.property
    def content(
        self,
    ) -> typing.Union[builtins.str, InputContent, typing.List[InputContent]]:
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(typing.Union[builtins.str, InputContent, typing.List[InputContent]], result)

    @builtins.property
    def role(self) -> builtins.str:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelContent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelDeltaOutput",
    jsii_struct_bases=[],
    name_mapping={
        "delta": "delta",
        "output_type": "outputType",
        "sequence_number": "sequenceNumber",
    },
)
class ModelDeltaOutput:
    def __init__(
        self,
        *,
        delta: builtins.str,
        output_type: builtins.str,
        sequence_number: jsii.Number,
    ) -> None:
        '''
        :param delta: 
        :param output_type: 
        :param sequence_number: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ebf203d1571bf36977de29383392461c96d558566559a744bfb6b33575fde2)
            check_type(argname="argument delta", value=delta, expected_type=type_hints["delta"])
            check_type(argname="argument output_type", value=output_type, expected_type=type_hints["output_type"])
            check_type(argname="argument sequence_number", value=sequence_number, expected_type=type_hints["sequence_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delta": delta,
            "output_type": output_type,
            "sequence_number": sequence_number,
        }

    @builtins.property
    def delta(self) -> builtins.str:
        result = self._values.get("delta")
        assert result is not None, "Required property 'delta' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_type(self) -> builtins.str:
        result = self._values.get("output_type")
        assert result is not None, "Required property 'output_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sequence_number(self) -> jsii.Number:
        result = self._values.get("sequence_number")
        assert result is not None, "Required property 'sequence_number' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelDeltaOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelResponse",
    jsii_struct_bases=[],
    name_mapping={
        "data": "data",
        "event_name": "eventName",
        "model_instance": "modelInstance",
        "thread_id": "threadId",
        "usage": "usage",
    },
)
class ModelResponse:
    def __init__(
        self,
        *,
        data: typing.Union[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union["ModelResponseData", typing.Dict[builtins.str, typing.Any]]]],
        event_name: builtins.str,
        model_instance: typing.Optional[IModel] = None,
        thread_id: typing.Optional[builtins.str] = None,
        usage: typing.Optional[typing.Union["Usage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param data: 
        :param event_name: 
        :param model_instance: 
        :param thread_id: 
        :param usage: 
        '''
        if isinstance(usage, dict):
            usage = Usage(**usage)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__109d6d097415cd9843b0740082bc89e3af273ab1f914ae31632c2d8cb02347f8)
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument event_name", value=event_name, expected_type=type_hints["event_name"])
            check_type(argname="argument model_instance", value=model_instance, expected_type=type_hints["model_instance"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument usage", value=usage, expected_type=type_hints["usage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data": data,
            "event_name": event_name,
        }
        if model_instance is not None:
            self._values["model_instance"] = model_instance
        if thread_id is not None:
            self._values["thread_id"] = thread_id
        if usage is not None:
            self._values["usage"] = usage

    @builtins.property
    def data(
        self,
    ) -> typing.Union["ModelResponseData", typing.List["ModelResponseData"]]:
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(typing.Union["ModelResponseData", typing.List["ModelResponseData"]], result)

    @builtins.property
    def event_name(self) -> builtins.str:
        result = self._values.get("event_name")
        assert result is not None, "Required property 'event_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_instance(self) -> typing.Optional[IModel]:
        result = self._values.get("model_instance")
        return typing.cast(typing.Optional[IModel], result)

    @builtins.property
    def thread_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("thread_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usage(self) -> typing.Optional["Usage"]:
        result = self._values.get("usage")
        return typing.cast(typing.Optional["Usage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelResponseData",
    jsii_struct_bases=[],
    name_mapping={
        "type_name": "typeName",
        "output_text": "outputText",
        "output_text_delta": "outputTextDelta",
        "requested": "requested",
        "thread_id": "threadId",
        "tool_call": "toolCall",
    },
)
class ModelResponseData:
    def __init__(
        self,
        *,
        type_name: builtins.str,
        output_text: typing.Optional[typing.Union["ModelTextOutput", typing.Dict[builtins.str, typing.Any]]] = None,
        output_text_delta: typing.Optional[typing.Union[ModelDeltaOutput, typing.Dict[builtins.str, typing.Any]]] = None,
        requested: typing.Any = None,
        thread_id: typing.Optional[builtins.str] = None,
        tool_call: typing.Optional[typing.Union["ModelToolOutput", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param type_name: 
        :param output_text: 
        :param output_text_delta: 
        :param requested: 
        :param thread_id: 
        :param tool_call: 
        '''
        if isinstance(output_text, dict):
            output_text = ModelTextOutput(**output_text)
        if isinstance(output_text_delta, dict):
            output_text_delta = ModelDeltaOutput(**output_text_delta)
        if isinstance(tool_call, dict):
            tool_call = ModelToolOutput(**tool_call)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c54b2668f4557f0584f65b073361f537a3099cafb0e3e975128080d63a876ad)
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument output_text", value=output_text, expected_type=type_hints["output_text"])
            check_type(argname="argument output_text_delta", value=output_text_delta, expected_type=type_hints["output_text_delta"])
            check_type(argname="argument requested", value=requested, expected_type=type_hints["requested"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument tool_call", value=tool_call, expected_type=type_hints["tool_call"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type_name": type_name,
        }
        if output_text is not None:
            self._values["output_text"] = output_text
        if output_text_delta is not None:
            self._values["output_text_delta"] = output_text_delta
        if requested is not None:
            self._values["requested"] = requested
        if thread_id is not None:
            self._values["thread_id"] = thread_id
        if tool_call is not None:
            self._values["tool_call"] = tool_call

    @builtins.property
    def type_name(self) -> builtins.str:
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_text(self) -> typing.Optional["ModelTextOutput"]:
        result = self._values.get("output_text")
        return typing.cast(typing.Optional["ModelTextOutput"], result)

    @builtins.property
    def output_text_delta(self) -> typing.Optional[ModelDeltaOutput]:
        result = self._values.get("output_text_delta")
        return typing.cast(typing.Optional[ModelDeltaOutput], result)

    @builtins.property
    def requested(self) -> typing.Any:
        result = self._values.get("requested")
        return typing.cast(typing.Any, result)

    @builtins.property
    def thread_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("thread_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tool_call(self) -> typing.Optional["ModelToolOutput"]:
        result = self._values.get("tool_call")
        return typing.cast(typing.Optional["ModelToolOutput"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelResponseData(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelResponseStreamValue",
    jsii_struct_bases=[],
    name_mapping={"done": "done", "value": "value"},
)
class ModelResponseStreamValue:
    def __init__(
        self,
        *,
        done: builtins.bool,
        value: typing.Optional[typing.Union[ModelResponse, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param done: 
        :param value: 
        '''
        if isinstance(value, dict):
            value = ModelResponse(**value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__393dc99748ce602c129bc849b3af84e539b3582bdee11093fb346e0f4d89c7ca)
            check_type(argname="argument done", value=done, expected_type=type_hints["done"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "done": done,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def done(self) -> builtins.bool:
        result = self._values.get("done")
        assert result is not None, "Required property 'done' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def value(self) -> typing.Optional[ModelResponse]:
        result = self._values.get("value")
        return typing.cast(typing.Optional[ModelResponse], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelResponseStreamValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelTextOutput",
    jsii_struct_bases=[],
    name_mapping={"output_type": "outputType", "text": "text"},
)
class ModelTextOutput:
    def __init__(self, *, output_type: builtins.str, text: builtins.str) -> None:
        '''
        :param output_type: 
        :param text: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ecbff96a5661f49f0150361a3ffaa42211ecc8b384ba31880b08a0af8aa8fe)
            check_type(argname="argument output_type", value=output_type, expected_type=type_hints["output_type"])
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "output_type": output_type,
            "text": text,
        }

    @builtins.property
    def output_type(self) -> builtins.str:
        result = self._values.get("output_type")
        assert result is not None, "Required property 'output_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text(self) -> builtins.str:
        result = self._values.get("text")
        assert result is not None, "Required property 'text' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelTextOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.ModelToolOutput",
    jsii_struct_bases=[],
    name_mapping={
        "arguments": "arguments",
        "call_id": "callId",
        "name": "name",
        "output_type": "outputType",
    },
)
class ModelToolOutput:
    def __init__(
        self,
        *,
        arguments: typing.Mapping[builtins.str, typing.Any],
        call_id: builtins.str,
        name: builtins.str,
        output_type: builtins.str,
    ) -> None:
        '''
        :param arguments: 
        :param call_id: 
        :param name: 
        :param output_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f800bf7fa9ac5c8fcc27fb7b41181d58eec75bccfa7714363f6fcac74ffa5582)
            check_type(argname="argument arguments", value=arguments, expected_type=type_hints["arguments"])
            check_type(argname="argument call_id", value=call_id, expected_type=type_hints["call_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument output_type", value=output_type, expected_type=type_hints["output_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arguments": arguments,
            "call_id": call_id,
            "name": name,
            "output_type": output_type,
        }

    @builtins.property
    def arguments(self) -> typing.Mapping[builtins.str, typing.Any]:
        result = self._values.get("arguments")
        assert result is not None, "Required property 'arguments' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def call_id(self) -> builtins.str:
        result = self._values.get("call_id")
        assert result is not None, "Required property 'call_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_type(self) -> builtins.str:
        result = self._values.get("output_type")
        assert result is not None, "Required property 'output_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelToolOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IOutcome)
class Outcomes(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Outcomes"):
    def __init__(self, outcomes: typing.Sequence[IOutcome]) -> None:
        '''
        :param outcomes: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331df68d79b2d604251f1008f76d8216ba94333ca3b50cdc1bdab02485bdcdcc)
            check_type(argname="argument outcomes", value=outcomes, expected_type=type_hints["outcomes"])
        jsii.create(self.__class__, self, [outcomes])

    @jsii.member(jsii_name="combine")
    @builtins.classmethod
    def combine(cls, *outcomes: IOutcome) -> "Outcomes":
        '''
        :param outcomes: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__598b522f067c9ba908694284b1a33d556dea82c28cb457a0893689b6a317270a)
            check_type(argname="argument outcomes", value=outcomes, expected_type=typing.Tuple[type_hints["outcomes"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Outcomes", jsii.sinvoke(cls, "combine", [*outcomes]))

    @jsii.member(jsii_name="bindToRequest")
    def bind_to_request(self, request: typing.Any) -> None:
        '''
        :param request: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3dbbdbae34fe5c4328e7f07ec5d5070f005978e7d666f836db6cf776d9496a9)
            check_type(argname="argument request", value=request, expected_type=type_hints["request"])
        return typing.cast(None, jsii.ainvoke(self, "bindToRequest", [request]))

    @jsii.member(jsii_name="send")
    def send(self, message_stream: IModelResponseStream) -> None:
        '''
        :param message_stream: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b042def1a191b2e91def0b062b7e9b29315a532c75421aa20a28ccf8ed60433d)
            check_type(argname="argument message_stream", value=message_stream, expected_type=type_hints["message_stream"])
        return typing.cast(None, jsii.ainvoke(self, "send", [message_stream]))


@jsii.data_type(
    jsii_type="@shuttl-io/core.OutputTokensDetails",
    jsii_struct_bases=[],
    name_mapping={"reasoning_tokens": "reasoningTokens"},
)
class OutputTokensDetails:
    def __init__(self, *, reasoning_tokens: jsii.Number) -> None:
        '''
        :param reasoning_tokens: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c175767976a8d29950732aaace9fd59145dcc5354ec2395d04d4e499debdffd4)
            check_type(argname="argument reasoning_tokens", value=reasoning_tokens, expected_type=type_hints["reasoning_tokens"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "reasoning_tokens": reasoning_tokens,
        }

    @builtins.property
    def reasoning_tokens(self) -> jsii.Number:
        result = self._values.get("reasoning_tokens")
        assert result is not None, "Required property 'reasoning_tokens' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OutputTokensDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Schema(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Schema"):
    @jsii.member(jsii_name="booleanValue")
    @builtins.classmethod
    def boolean_value(cls, description: builtins.str) -> "ToolArgBuilder":
        '''
        :param description: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__337efa37832574be0a930ba07860f808daff0dd38ff876af83acdceae521da21)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast("ToolArgBuilder", jsii.sinvoke(cls, "booleanValue", [description]))

    @jsii.member(jsii_name="enumValue")
    @builtins.classmethod
    def enum_value(
        cls,
        description: builtins.str,
        enum_values: typing.Sequence[builtins.str],
    ) -> "ToolArgBuilder":
        '''
        :param description: -
        :param enum_values: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56946bef7594a7a59a171969b0175368edb02969935a81a7e00eeb7a7c460e60)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument enum_values", value=enum_values, expected_type=type_hints["enum_values"])
        return typing.cast("ToolArgBuilder", jsii.sinvoke(cls, "enumValue", [description, enum_values]))

    @jsii.member(jsii_name="numberValue")
    @builtins.classmethod
    def number_value(cls, description: builtins.str) -> "ToolArgBuilder":
        '''
        :param description: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99c575dc2bf0e46be85e377f2eae4d0c3db9c7b83a978b5ec60ac8d13dc2517)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast("ToolArgBuilder", jsii.sinvoke(cls, "numberValue", [description]))

    @jsii.member(jsii_name="objectValue")
    @builtins.classmethod
    def object_value(
        cls,
        properties: typing.Mapping[builtins.str, "ToolArgBuilder"],
    ) -> "Schema":
        '''
        :param properties: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ec81e5158cef1e29b2d84cd99ca741cc93d8fb92b1acc75436519e3e9e2dd73)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        return typing.cast("Schema", jsii.sinvoke(cls, "objectValue", [properties]))

    @jsii.member(jsii_name="stringValue")
    @builtins.classmethod
    def string_value(cls, description: builtins.str) -> "ToolArgBuilder":
        '''
        :param description: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e762563132c59d170d9506afea7380ed3b7994ca53a51560066a4a450b033cca)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast("ToolArgBuilder", jsii.sinvoke(cls, "stringValue", [description]))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, "ToolArgBuilder"]:
        return typing.cast(typing.Mapping[builtins.str, "ToolArgBuilder"], jsii.get(self, "properties"))


class Secret(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Secret"):
    @jsii.member(jsii_name="fromEnv")
    @builtins.classmethod
    def from_env(cls, env_var_name: builtins.str) -> ISecret:
        '''Create a Secret from an environment variable.

        :param env_var_name: The name of the environment variable.

        :return: A new Secret.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2437b3aa89a027644df9310c8729ef07d53b6af01dc5327ba86d172b163772b)
            check_type(argname="argument env_var_name", value=env_var_name, expected_type=type_hints["env_var_name"])
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromEnv", [env_var_name]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__743f4c3e2ca189338dab8fe52db0739a5dc03deeda7f778525f47b74d895d927)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__241e5fe2d5635c23f63b68933e24dc247545f3c5a32e6287b6dd7589aff6865b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@shuttl-io/core.SerializedHTTPRequest",
    jsii_struct_bases=[],
    name_mapping={
        "content_type": "contentType",
        "headers": "headers",
        "host": "host",
        "method": "method",
        "path": "path",
        "proto": "proto",
        "query": "query",
        "remote_addr": "remoteAddr",
        "timestamp": "timestamp",
        "body": "body",
    },
)
class SerializedHTTPRequest:
    def __init__(
        self,
        *,
        content_type: builtins.str,
        headers: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
        host: builtins.str,
        method: builtins.str,
        path: builtins.str,
        proto: builtins.str,
        query: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
        remote_addr: builtins.str,
        timestamp: builtins.str,
        body: typing.Any = None,
    ) -> None:
        '''Represents a serialized HTTP request from the serve command.

        :param content_type: The Content-Type header value.
        :param headers: HTTP headers as key-value pairs with array values.
        :param host: The host header value.
        :param method: The HTTP method (POST, GET, etc.).
        :param path: The request path.
        :param proto: The HTTP protocol version.
        :param query: Query parameters as key-value pairs with array values.
        :param remote_addr: The remote address of the client.
        :param timestamp: Timestamp of when the request was received.
        :param body: The request body (parsed JSON or raw).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4c53989901d0db5847a7331c18063736cafe25e10dd820001512d6321c8a25)
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument proto", value=proto, expected_type=type_hints["proto"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
            check_type(argname="argument remote_addr", value=remote_addr, expected_type=type_hints["remote_addr"])
            check_type(argname="argument timestamp", value=timestamp, expected_type=type_hints["timestamp"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content_type": content_type,
            "headers": headers,
            "host": host,
            "method": method,
            "path": path,
            "proto": proto,
            "query": query,
            "remote_addr": remote_addr,
            "timestamp": timestamp,
        }
        if body is not None:
            self._values["body"] = body

    @builtins.property
    def content_type(self) -> builtins.str:
        '''The Content-Type header value.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def headers(self) -> typing.Mapping[builtins.str, typing.List[builtins.str]]:
        '''HTTP headers as key-value pairs with array values.'''
        result = self._values.get("headers")
        assert result is not None, "Required property 'headers' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.List[builtins.str]], result)

    @builtins.property
    def host(self) -> builtins.str:
        '''The host header value.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> builtins.str:
        '''The HTTP method (POST, GET, etc.).'''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''The request path.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proto(self) -> builtins.str:
        '''The HTTP protocol version.'''
        result = self._values.get("proto")
        assert result is not None, "Required property 'proto' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query(self) -> typing.Mapping[builtins.str, typing.List[builtins.str]]:
        '''Query parameters as key-value pairs with array values.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.List[builtins.str]], result)

    @builtins.property
    def remote_addr(self) -> builtins.str:
        '''The remote address of the client.'''
        result = self._values.get("remote_addr")
        assert result is not None, "Required property 'remote_addr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp(self) -> builtins.str:
        '''Timestamp of when the request was received.'''
        result = self._values.get("timestamp")
        assert result is not None, "Required property 'timestamp' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Any:
        '''The request body (parsed JSON or raw).'''
        result = self._values.get("body")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SerializedHTTPRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IOutcome)
class SlackOutcome(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.SlackOutcome"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bindToRequest")
    def bind_to_request(self, request: typing.Any) -> None:
        '''
        :param request: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2934629c2c7c1cf8c4785cc747882d6fdf2ba9b87a17d9cc5abd98edeaa7f020)
            check_type(argname="argument request", value=request, expected_type=type_hints["request"])
        return typing.cast(None, jsii.ainvoke(self, "bindToRequest", [request]))

    @jsii.member(jsii_name="send")
    def send(self, message_stream: IModelResponseStream) -> None:
        '''
        :param message_stream: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccab3bbdeba137213879e53553cfb63633ea0532f887d6aee8c69e5e0f801d73)
            check_type(argname="argument message_stream", value=message_stream, expected_type=type_hints["message_stream"])
        return typing.cast(None, jsii.ainvoke(self, "send", [message_stream]))


@jsii.implements(IServer)
class StdInServer(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.StdInServer"):
    '''A server that communicates via STDIN/STDOUT using JSON messages.

    Uses newline-delimited JSON (NDJSON) protocol where each message
    is a single line of JSON followed by a newline character.

    Host CLI writes requests to the process's STDIN.
    This server writes responses to STDOUT.
    Debug/log messages go to STDERR to avoid polluting the protocol.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="accept")
    def accept(self, app: typing.Any) -> None:
        '''
        :param app: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118a405d22ce0f329d0c754a65e2dba723eccae601c98ef1274c1226d2e656e0)
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
        return typing.cast(None, jsii.invoke(self, "accept", [app]))

    @jsii.member(jsii_name="start")
    def start(self) -> None:
        return typing.cast(None, jsii.ainvoke(self, "start", []))

    @jsii.member(jsii_name="stop")
    def stop(self) -> None:
        return typing.cast(None, jsii.ainvoke(self, "stop", []))


@jsii.implements(IOutcome)
class StreamingOutcome(
    metaclass=jsii.JSIIMeta,
    jsii_type="@shuttl-io/core.StreamingOutcome",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bindToRequest")
    def bind_to_request(self, request: typing.Any) -> None:
        '''
        :param request: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0c465a26a01e4d43a35965d9ee77ffcb88c791c0fa8062aa1c3f4b861e53238)
            check_type(argname="argument request", value=request, expected_type=type_hints["request"])
        return typing.cast(None, jsii.ainvoke(self, "bindToRequest", [request]))

    @jsii.member(jsii_name="send")
    def send(self, message_stream: IModelResponseStream) -> None:
        '''
        :param message_stream: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6086ef18de2713f1fa28ad9d6c41768205de3085d67df665c2dc9a710171f38a)
            check_type(argname="argument message_stream", value=message_stream, expected_type=type_hints["message_stream"])
        return typing.cast(None, jsii.ainvoke(self, "send", [message_stream]))


@jsii.data_type(
    jsii_type="@shuttl-io/core.ToolArg",
    jsii_struct_bases=[],
    name_mapping={
        "arg_type": "argType",
        "description": "description",
        "required": "required",
        "default_value": "defaultValue",
        "enum_values": "enumValues",
        "name": "name",
    },
)
class ToolArg:
    def __init__(
        self,
        *,
        arg_type: builtins.str,
        description: builtins.str,
        required: builtins.bool,
        default_value: typing.Any = None,
        enum_values: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param arg_type: 
        :param description: 
        :param required: 
        :param default_value: 
        :param enum_values: 
        :param name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f41336a4bb494a65c8d528170cdcac4f05c0dcc665485171121f3cb0841b6555)
            check_type(argname="argument arg_type", value=arg_type, expected_type=type_hints["arg_type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
            check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
            check_type(argname="argument enum_values", value=enum_values, expected_type=type_hints["enum_values"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arg_type": arg_type,
            "description": description,
            "required": required,
        }
        if default_value is not None:
            self._values["default_value"] = default_value
        if enum_values is not None:
            self._values["enum_values"] = enum_values
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def arg_type(self) -> builtins.str:
        result = self._values.get("arg_type")
        assert result is not None, "Required property 'arg_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def required(self) -> builtins.bool:
        result = self._values.get("required")
        assert result is not None, "Required property 'required' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def default_value(self) -> typing.Any:
        result = self._values.get("default_value")
        return typing.cast(typing.Any, result)

    @builtins.property
    def enum_values(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("enum_values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ToolArg(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ToolArgBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@shuttl-io/core.ToolArgBuilder",
):
    def __init__(
        self,
        arg_type: builtins.str,
        description: builtins.str,
        required: builtins.bool,
        default_value: typing.Any = None,
        enum_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param arg_type: -
        :param description: -
        :param required: -
        :param default_value: -
        :param enum_values: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c98ca3ddf4b0c4129b298763d1682fbb70e2e6262acf5aa904a8cce74b6b7f1)
            check_type(argname="argument arg_type", value=arg_type, expected_type=type_hints["arg_type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
            check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
            check_type(argname="argument enum_values", value=enum_values, expected_type=type_hints["enum_values"])
        jsii.create(self.__class__, self, [arg_type, description, required, default_value, enum_values])

    @jsii.member(jsii_name="defaultTo")
    def default_to(self, default_value: typing.Any) -> "ToolArgBuilder":
        '''
        :param default_value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02cc88fbf77ef89a25714c7df17626d7770131b8e93b08511ebd5eac7023bd7b)
            check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
        return typing.cast("ToolArgBuilder", jsii.invoke(self, "defaultTo", [default_value]))

    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> "ToolArgBuilder":
        return typing.cast("ToolArgBuilder", jsii.invoke(self, "isRequired", []))

    @builtins.property
    @jsii.member(jsii_name="argType")
    def arg_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "argType"))

    @arg_type.setter
    def arg_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77dc06e59f474d15e254bb52b0b8280d4f126df3f70beebff711224088e10443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__223fa643d31a84059e93a1975ec7653e74cd3d6f844d52a3e3438d24eec185f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "required"))

    @required.setter
    def required(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8689cc83c8cc51b6578926a75b25e451bc7a70d90e040252d09b93d13043dde9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultValue")
    def default_value(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "defaultValue"))

    @default_value.setter
    def default_value(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bbe183442610cb90c67a7b6c863fc4f25a80dca6d77b1fe96aee423a47bf48f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enumValues")
    def enum_values(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enumValues"))

    @enum_values.setter
    def enum_values(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40f14e0d1265b816872562f3db5d1d489e92ed9497e3f07978e2812938d172de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enumValues", value) # pyright: ignore[reportArgumentType]


class Toolkit(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Toolkit"):
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tools: typing.Optional[typing.Sequence[ITool]] = None,
    ) -> None:
        '''
        :param name: 
        :param description: 
        :param tools: 
        '''
        props = ToolkitProps(name=name, description=description, tools=tools)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addTool")
    def add_tool(self, tool: ITool) -> None:
        '''
        :param tool: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b06cb7c0c8ed9b5a89f4ac05fe513ec187bb25c73068fdbb1d66d69c5f56cf8)
            check_type(argname="argument tool", value=tool, expected_type=type_hints["tool"])
        return typing.cast(None, jsii.invoke(self, "addTool", [tool]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="tools")
    def tools(self) -> typing.List[ITool]:
        return typing.cast(typing.List[ITool], jsii.get(self, "tools"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))


@jsii.data_type(
    jsii_type="@shuttl-io/core.ToolkitProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description", "tools": "tools"},
)
class ToolkitProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tools: typing.Optional[typing.Sequence[ITool]] = None,
    ) -> None:
        '''
        :param name: 
        :param description: 
        :param tools: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78c15c77c5fb27e5906320c6e31991181c025de9f1555f4db2f3745fb02461b8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument tools", value=tools, expected_type=type_hints["tools"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if tools is not None:
            self._values["tools"] = tools

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tools(self) -> typing.Optional[typing.List[ITool]]:
        result = self._values.get("tools")
        return typing.cast(typing.Optional[typing.List[ITool]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ToolkitProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.TriggerOutput",
    jsii_struct_bases=[],
    name_mapping={"input": "input"},
)
class TriggerOutput:
    def __init__(
        self,
        *,
        input: typing.Sequence[typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param input: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17db2b7203ff1eaa3855703200b93e2aee61ae9f9eb8cea8d3e52306ff2d8b58)
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "input": input,
        }

    @builtins.property
    def input(self) -> typing.List[InputContent]:
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(typing.List[InputContent], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggerOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@shuttl-io/core.Usage",
    jsii_struct_bases=[],
    name_mapping={
        "input_tokens": "inputTokens",
        "input_tokens_details": "inputTokensDetails",
        "output_tokens": "outputTokens",
        "output_tokens_details": "outputTokensDetails",
        "total_tokens": "totalTokens",
    },
)
class Usage:
    def __init__(
        self,
        *,
        input_tokens: jsii.Number,
        input_tokens_details: typing.Union[InputTokensDetails, typing.Dict[builtins.str, typing.Any]],
        output_tokens: jsii.Number,
        output_tokens_details: typing.Union[OutputTokensDetails, typing.Dict[builtins.str, typing.Any]],
        total_tokens: jsii.Number,
    ) -> None:
        '''
        :param input_tokens: 
        :param input_tokens_details: 
        :param output_tokens: 
        :param output_tokens_details: 
        :param total_tokens: 
        '''
        if isinstance(input_tokens_details, dict):
            input_tokens_details = InputTokensDetails(**input_tokens_details)
        if isinstance(output_tokens_details, dict):
            output_tokens_details = OutputTokensDetails(**output_tokens_details)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d24de8f601f1c379d26db5ebe48f48ba5dc5abed10b1441c4faee68c2035a9eb)
            check_type(argname="argument input_tokens", value=input_tokens, expected_type=type_hints["input_tokens"])
            check_type(argname="argument input_tokens_details", value=input_tokens_details, expected_type=type_hints["input_tokens_details"])
            check_type(argname="argument output_tokens", value=output_tokens, expected_type=type_hints["output_tokens"])
            check_type(argname="argument output_tokens_details", value=output_tokens_details, expected_type=type_hints["output_tokens_details"])
            check_type(argname="argument total_tokens", value=total_tokens, expected_type=type_hints["total_tokens"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "input_tokens": input_tokens,
            "input_tokens_details": input_tokens_details,
            "output_tokens": output_tokens,
            "output_tokens_details": output_tokens_details,
            "total_tokens": total_tokens,
        }

    @builtins.property
    def input_tokens(self) -> jsii.Number:
        result = self._values.get("input_tokens")
        assert result is not None, "Required property 'input_tokens' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def input_tokens_details(self) -> InputTokensDetails:
        result = self._values.get("input_tokens_details")
        assert result is not None, "Required property 'input_tokens_details' is missing"
        return typing.cast(InputTokensDetails, result)

    @builtins.property
    def output_tokens(self) -> jsii.Number:
        result = self._values.get("output_tokens")
        assert result is not None, "Required property 'output_tokens' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def output_tokens_details(self) -> OutputTokensDetails:
        result = self._values.get("output_tokens_details")
        assert result is not None, "Required property 'output_tokens_details' is missing"
        return typing.cast(OutputTokensDetails, result)

    @builtins.property
    def total_tokens(self) -> jsii.Number:
        result = self._values.get("total_tokens")
        assert result is not None, "Required property 'total_tokens' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Usage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IModelStreamer)
class AgentStreamer(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.AgentStreamer"):
    def __init__(
        self,
        agent: Agent,
        control_id: builtins.str,
        writer: typing.Optional[IAgentStreamerWriter] = None,
    ) -> None:
        '''
        :param agent: -
        :param control_id: -
        :param writer: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a780658982bd5d1f55e11fc56e862fea30e03665792aaab265d749d583fbda17)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument control_id", value=control_id, expected_type=type_hints["control_id"])
            check_type(argname="argument writer", value=writer, expected_type=type_hints["writer"])
        jsii.create(self.__class__, self, [agent, control_id, writer])

    @jsii.member(jsii_name="recieve")
    def recieve(
        self,
        model: IModel,
        *,
        data: typing.Union[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]]]],
        event_name: builtins.str,
        model_instance: typing.Optional[IModel] = None,
        thread_id: typing.Optional[builtins.str] = None,
        usage: typing.Optional[typing.Union[Usage, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param model: -
        :param data: 
        :param event_name: 
        :param model_instance: 
        :param thread_id: 
        :param usage: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b617812079844c0447bec9a50b46ab48a3ff26e6568affb34fe2994d43bd8ab)
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
        content = ModelResponse(
            data=data,
            event_name=event_name,
            model_instance=model_instance,
            thread_id=thread_id,
            usage=usage,
        )

        return typing.cast(None, jsii.ainvoke(self, "recieve", [model, content]))


@jsii.implements(ITrigger)
class BaseTrigger(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@shuttl-io/core.BaseTrigger",
):
    def __init__(
        self,
        trigger_type: builtins.str,
        config: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        '''
        :param trigger_type: The type of trigger.
        :param config: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69c4f6318d18b1e977da3ef51f3b9af27d73469e46aa556ea686ae3f36405a01)
            check_type(argname="argument trigger_type", value=trigger_type, expected_type=type_hints["trigger_type"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
        jsii.create(self.__class__, self, [trigger_type, config])

    @jsii.member(jsii_name="activate")
    def activate(self, args: typing.Any, invoker: ITriggerInvoker) -> None:
        '''Activates the trigger and returns the input for the agent.

        :param args: -
        :param invoker: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0460df3be8bc538f91d112e240db7568e5b3d3966b63378cd56cc592cab951a5)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
            check_type(argname="argument invoker", value=invoker, expected_type=type_hints["invoker"])
        return typing.cast(None, jsii.ainvoke(self, "activate", [args, invoker]))

    @jsii.member(jsii_name="bindOutcome")
    def bind_outcome(self, outcome: IOutcome) -> ITrigger:
        '''binds the outcome to the trigger.

        :param outcome: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfbb0dd47e0631db7f92e7ce94e70a889b2e5d86f362abcea5831681f3b46f37)
            check_type(argname="argument outcome", value=outcome, expected_type=type_hints["outcome"])
        return typing.cast(ITrigger, jsii.invoke(self, "bindOutcome", [outcome]))

    @jsii.member(jsii_name="parseArgs")
    @abc.abstractmethod
    def parse_args(self, args: typing.Any) -> TriggerOutput:
        '''
        :param args: -
        '''
        ...

    @jsii.member(jsii_name="validate")
    def validate(self, _: typing.Any) -> typing.Mapping[builtins.str, typing.Any]:
        '''Validates the arguments for the trigger.

        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3acdf7981e6153485061b7dd1a4923908be61b4d27808083e8feaa1187a38b9d)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.ainvoke(self, "validate", [_]))

    @jsii.member(jsii_name="withName")
    def with_name(self, name: builtins.str) -> ITrigger:
        '''Sets the name of the trigger.

        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0731fe7110cc1750189e0b484b0b795c75c45539bf5cbdb618f4551731f1ac19)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(ITrigger, jsii.invoke(self, "withName", [name]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The unique name of this trigger instance.

        If not set, defaults to triggerType.
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9431eaf07533872c8ce0c381fd73c45ae8ce9bf29b333d7c2e5ef9e7fc807e7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerConfig")
    def trigger_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The configuration for the trigger.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "triggerConfig"))

    @trigger_config.setter
    def trigger_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cec5b169a731613f477373f14eb05a5003c1ade1162a97a21cac65d0f2e19c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccf6278f3562d7eccc209e87ba94ee9b0be3ad48fa162d720d80886dd6b36542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b96315ac801eb7de8b68f35fbec17b578bb0ede23311b39e3f27c08601c0d35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]


class _BaseTriggerProxy(BaseTrigger):
    @jsii.member(jsii_name="parseArgs")
    def parse_args(self, args: typing.Any) -> TriggerOutput:
        '''
        :param args: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4aeffa2e17eb557454896a5f34d88a69e6fc6848ea3f5815fc65b22c77a675c)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        return typing.cast(TriggerOutput, jsii.ainvoke(self, "parseArgs", [args]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseTrigger).__jsii_proxy_class__ = lambda : _BaseTriggerProxy


class EmailTrigger(
    BaseTrigger,
    metaclass=jsii.JSIIMeta,
    jsii_type="@shuttl-io/core.EmailTrigger",
):
    def __init__(
        self,
        *,
        domain: builtins.str,
        folder: builtins.str,
        from_address: builtins.str,
        inbox_name: builtins.str,
        subject_pattern: builtins.str,
    ) -> None:
        '''
        :param domain: 
        :param folder: 
        :param from_address: 
        :param inbox_name: 
        :param subject_pattern: 
        '''
        config = EmailTriggerConfig(
            domain=domain,
            folder=folder,
            from_address=from_address,
            inbox_name=inbox_name,
            subject_pattern=subject_pattern,
        )

        jsii.create(self.__class__, self, [config])

    @jsii.member(jsii_name="parseArgs")
    def parse_args(self, _: typing.Any) -> TriggerOutput:
        '''
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4fd64b2be233cee8fa53ee91cd845e023db430682dc5b33ded79d9325b25bc1)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(TriggerOutput, jsii.ainvoke(self, "parseArgs", [_]))

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50dee7e2c033feea222996f74baf3b87256b409b4975193a1b848683291f8864)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e77d3494dba54add6254b36be0222ee5b094a3c391b3c8db59ae732586a18cbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ISecret)
class EnvSecret(metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.EnvSecret"):
    def __init__(self, env_var_name: builtins.str) -> None:
        '''
        :param env_var_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc668fd428f011951dda414673ee6c295893590ae107ca4e03b411b4749f135)
            check_type(argname="argument env_var_name", value=env_var_name, expected_type=type_hints["env_var_name"])
        jsii.create(self.__class__, self, [env_var_name])

    @jsii.member(jsii_name="resolveSecret")
    def resolve_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.ainvoke(self, "resolveSecret", []))

    @builtins.property
    @jsii.member(jsii_name="envVarName")
    def env_var_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "envVarName"))


class FileTrigger(
    BaseTrigger,
    metaclass=jsii.JSIIMeta,
    jsii_type="@shuttl-io/core.FileTrigger",
):
    def __init__(
        self,
        *,
        allowed_extensions: typing.Sequence[builtins.str],
        max_file_size: jsii.Number,
        s3_bucket: builtins.str,
        upload_path: builtins.str,
    ) -> None:
        '''
        :param allowed_extensions: 
        :param max_file_size: 
        :param s3_bucket: 
        :param upload_path: 
        '''
        config = FileTriggerConfig(
            allowed_extensions=allowed_extensions,
            max_file_size=max_file_size,
            s3_bucket=s3_bucket,
            upload_path=upload_path,
        )

        jsii.create(self.__class__, self, [config])

    @jsii.member(jsii_name="parseArgs")
    def parse_args(self, args: typing.Any) -> TriggerOutput:
        '''
        :param args: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fd1f615c38c637344765af93fb3efe0fc6590599dcef067eb99953f9c2df1d6)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        return typing.cast(TriggerOutput, jsii.ainvoke(self, "parseArgs", [args]))

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdf8fdf30315ae18ef201cfcc892f2d043338174d93e6f0d6e6f8169bce4da96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca934182ee092baa0a7df9356d4366e8ab836dacb02ef5fda09aa7e9cf48f6d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]


class Rate(BaseTrigger, metaclass=jsii.JSIIMeta, jsii_type="@shuttl-io/core.Rate"):
    @jsii.member(jsii_name="cron")
    @builtins.classmethod
    def cron(
        cls,
        expression: builtins.str,
        timezone: typing.Optional[builtins.str] = None,
    ) -> "Rate":
        '''
        :param expression: -
        :param timezone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03c1a949ace1c3265367b3fd4ae539d8bde8097a12ff708d0ea375676e13d504)
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
        return typing.cast("Rate", jsii.sinvoke(cls, "cron", [expression, timezone]))

    @jsii.member(jsii_name="days")
    @builtins.classmethod
    def days(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c779aee66496c0494c7fb04f76fea9fa7cc2c0fbb87ea9afc080c8f6d3140872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "days", [value]))

    @jsii.member(jsii_name="hours")
    @builtins.classmethod
    def hours(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1875e8f138c3e91e337a0ddb269b9cf391e706bb1575836cc4ad5109de8d268a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "hours", [value]))

    @jsii.member(jsii_name="milliseconds")
    @builtins.classmethod
    def milliseconds(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11c22831d95c2b0dc4c8784a0be7ea2ebd7131ba74b1cdc9c58625ba45a85595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "milliseconds", [value]))

    @jsii.member(jsii_name="minutes")
    @builtins.classmethod
    def minutes(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322868d921ba17e7302996e348bf5124bd4e777808b91f2d1f351c5a58fe0d35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "minutes", [value]))

    @jsii.member(jsii_name="months")
    @builtins.classmethod
    def months(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3db5c6b3801023a3beddc82a4e106fefbc4fd9b8c7d6c9ed34af57b6929f7f9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "months", [value]))

    @jsii.member(jsii_name="seconds")
    @builtins.classmethod
    def seconds(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80180bc210ca4651ac4a33c6d4c8eef0b95793fcfe80fbadcc175bce68f38702)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "seconds", [value]))

    @jsii.member(jsii_name="weeks")
    @builtins.classmethod
    def weeks(cls, value: jsii.Number) -> "Rate":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e829c4357695b945edd9de3c22fd6bc66b0560de5c0152b7497d44104875165)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Rate", jsii.sinvoke(cls, "weeks", [value]))

    @jsii.member(jsii_name="parseArgs")
    def parse_args(self, _: typing.Any) -> TriggerOutput:
        '''
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c04ed9f932e4ea690e653fb9c5becc1d7785968ded123fbaff6a0c2172df492)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(TriggerOutput, jsii.ainvoke(self, "parseArgs", [_]))

    @jsii.member(jsii_name="withOnTrigger")
    def with_on_trigger(self, on_trigger: IRateTriggerOnTrigger) -> "Rate":
        '''
        :param on_trigger: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f722247541d2a4dee16b3d314647938f2a8984c337a09d02dee6c25858855c0)
            check_type(argname="argument on_trigger", value=on_trigger, expected_type=type_hints["on_trigger"])
        return typing.cast("Rate", jsii.invoke(self, "withOnTrigger", [on_trigger]))

    @builtins.property
    @jsii.member(jsii_name="triggerConfig")
    def trigger_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The configuration for the trigger.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "triggerConfig"))

    @trigger_config.setter
    def trigger_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78bfccbd1a3f1ccbe5fb53092d0fcc5bf7386096bdabbba6adf3c4d0aadb3d8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc520d78b3b42e47e38a737482fd2144e377da18d6b3bf66d3cbb5464b2d107c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c24fc0088fcc90db55b7a025b3041bf7b4b13a1dcb77acba8e4c0938c8803879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]


class ApiTrigger(
    BaseTrigger,
    metaclass=jsii.JSIIMeta,
    jsii_type="@shuttl-io/core.ApiTrigger",
):
    '''Represents a trigger that can activate an agent via an API call.

    This API trigger is the default trigger for agents.
    '''

    def __init__(
        self,
        *,
        authenticator: typing.Optional[IApiAuthenticator] = None,
        cors: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param authenticator: 
        :param cors: 
        '''
        config = ApiTriggerConfig(authenticator=authenticator, cors=cors)

        jsii.create(self.__class__, self, [config])

    @jsii.member(jsii_name="parseArgs")
    def parse_args(self, raw_args: typing.Any) -> TriggerOutput:
        '''
        :param raw_args: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a10624edec3cdb1b33d3c494fd5ef6bb901feed8f69d7f9f3304039ee65b2232)
            check_type(argname="argument raw_args", value=raw_args, expected_type=type_hints["raw_args"])
        return typing.cast(TriggerOutput, jsii.ainvoke(self, "parseArgs", [raw_args]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        raw_args: typing.Any,
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''Validates the arguments for the trigger.

        :param raw_args: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ff5c668bcefd2b18cbbe03a38c3b095b5793c7204f0853a0552228673aa0e7)
            check_type(argname="argument raw_args", value=raw_args, expected_type=type_hints["raw_args"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.ainvoke(self, "validate", [raw_args]))

    @builtins.property
    @jsii.member(jsii_name="triggerConfig")
    def trigger_config(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''The configuration for the trigger.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "triggerConfig"))

    @trigger_config.setter
    def trigger_config(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e8fd5cca79988489e2997902e7b263d688282e0d84c36aa6f1eabe8e1248074)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggerType")
    def trigger_type(self) -> builtins.str:
        '''The type of trigger.'''
        return typing.cast(builtins.str, jsii.get(self, "triggerType"))

    @trigger_type.setter
    def trigger_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d920fae9073c220b4f180598c9916ed9fa80978689ff64bc2d8239b6f5aa17a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outcome")
    def outcome(self) -> typing.Optional[IOutcome]:
        return typing.cast(typing.Optional[IOutcome], jsii.get(self, "outcome"))

    @outcome.setter
    def outcome(self, value: typing.Optional[IOutcome]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f77a7ac81bb04ddbda4879fffdad73a5435d8b8239902789e347a76bc78dcd0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outcome", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Agent",
    "AgentProps",
    "AgentStreamer",
    "ApiAuth",
    "ApiTrigger",
    "ApiTriggerArgs",
    "ApiTriggerConfig",
    "App",
    "BaseTrigger",
    "EmailTrigger",
    "EmailTriggerConfig",
    "EnvSecret",
    "FileAttachment",
    "FileTrigger",
    "FileTriggerConfig",
    "IAgentStreamerWriter",
    "IApiAuthenticator",
    "IModel",
    "IModelFactory",
    "IModelFactoryProps",
    "IModelResponseStream",
    "IModelStreamer",
    "IOutcome",
    "IPCRequest",
    "IPCResponse",
    "IPCResponseError",
    "IRateTriggerOnTrigger",
    "ISecret",
    "IServer",
    "ITool",
    "ITrigger",
    "ITriggerInvoker",
    "InputContent",
    "InputTokensDetails",
    "Model",
    "ModelContent",
    "ModelDeltaOutput",
    "ModelResponse",
    "ModelResponseData",
    "ModelResponseStreamValue",
    "ModelTextOutput",
    "ModelToolOutput",
    "Outcomes",
    "OutputTokensDetails",
    "Rate",
    "Schema",
    "Secret",
    "SerializedHTTPRequest",
    "SlackOutcome",
    "StdInServer",
    "StreamingOutcome",
    "ToolArg",
    "ToolArgBuilder",
    "Toolkit",
    "ToolkitProps",
    "TriggerOutput",
    "Usage",
]

publication.publish()

def _typecheckingstub__c5684bbdd0bbef8364213afb90164f887c379eb6c02b9fb4a222dc55866f49c5(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c357f1d52dc825b09805321f8c2577ebf97109bfc5f58c2bc8dbe6658ad8bbc2(
    call_id: builtins.str,
    result: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bc8d5e10d3458b7f0128af31d93991e3603b23cf6306a2afcd6f472183b1e86(
    prompt: typing.Union[builtins.str, typing.Sequence[typing.Union[typing.Union[ModelContent, typing.Dict[builtins.str, typing.Any]], typing.Mapping[builtins.str, typing.Any]]]],
    thread_id: typing.Optional[builtins.str] = None,
    streamer: typing.Optional[IModelStreamer] = None,
    attachments: typing.Optional[typing.Sequence[typing.Union[FileAttachment, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a426ad5ea12640cf63723199dd1f1999153da07b4cf299a7819e87abb23f544f(
    model_instance: IModel,
    call_id: builtins.str,
    result: typing.Any,
    streamer: IModelStreamer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__772e09ef2798d90b831b5cd341522046082132dc43579d76188b9ddd9e90a3d7(
    *,
    model: IModelFactory,
    name: builtins.str,
    system_prompt: builtins.str,
    toolkits: typing.Sequence[Toolkit],
    outcomes: typing.Optional[typing.Sequence[IOutcome]] = None,
    tools: typing.Optional[typing.Sequence[ITool]] = None,
    triggers: typing.Optional[typing.Sequence[ITrigger]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e802366751dd7472ced51de248ecdc5d45fcc2095126a20b69b505a251b5663(
    *,
    auth_type: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed9cbe1300a30dc34c2bb84fa4e0ca9f5b14d80762e1f50699d6979dfd1ead0(
    *,
    host_name: builtins.str,
    method: builtins.str,
    auth: typing.Optional[typing.Union[ApiAuth, typing.Dict[builtins.str, typing.Any]]] = None,
    body: typing.Any = None,
    cookies: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    path_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    query_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f4f099b44cc988eb7dbbe99a2ebb3e4b4bdb5f969533a1172f12bd926d2872(
    *,
    authenticator: typing.Optional[IApiAuthenticator] = None,
    cors: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43533246dc785273087a131e3882a92eecb170c828986e171d107be193116a40(
    name: builtins.str,
    server: IServer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01984d81fd457408a23c7e84fee151b085ed90597fd46465a123b5f1b19e1acf(
    agent: Agent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e1cd21702140418dddee57370c5464866f4bc61178c6ba157d0d0e06390222c(
    toolkit: Toolkit,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2a98b590bd52775dda41ea08af1f5c079e64d60814426456f202c906a70db2(
    *,
    domain: builtins.str,
    folder: builtins.str,
    from_address: builtins.str,
    inbox_name: builtins.str,
    subject_pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b87a01c828afa7d42dfa3adc5e53bbd3d07b84a17f5d3e4b84c1f727f075bd(
    *,
    content: builtins.str,
    name: builtins.str,
    mime_type: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca8007b7d694698dff28eaa147f22cfb1a74b3acd1ed88eea72bb85c856a88e4(
    *,
    allowed_extensions: typing.Sequence[builtins.str],
    max_file_size: jsii.Number,
    s3_bucket: builtins.str,
    upload_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d789e8211b96d69d0d9dc11552926a41d95d137bd4c834683889acdf03d85853(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf7804ae8cd0b2e0bd19aefffc531c49792898e187bcffec35172beddbea7ab(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc0405cb1c62c8c0f09fc66cc0baf65b1eb2a40772e4d1c3c18c375e177ae81(
    prompt: typing.Sequence[typing.Union[typing.Union[ModelContent, typing.Dict[builtins.str, typing.Any]], typing.Mapping[builtins.str, typing.Any]]],
    streamer: IModelStreamer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a43295bce67af72272e842a02d29a142058c39c0e1ffab0ea8278f4bdf090fd(
    props: IModelFactoryProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f653d3d9c6c4d52acd8e641a6063e4a96b1a83995e001c2dd0e736cbe04634(
    model: IModel,
    *,
    data: typing.Union[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]]]],
    event_name: builtins.str,
    model_instance: typing.Optional[IModel] = None,
    thread_id: typing.Optional[builtins.str] = None,
    usage: typing.Optional[typing.Union[Usage, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd6fa69a7f3da5347340534c57cb92847212c71d6f93a48fee96d4f6c7ed87a9(
    request: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3263f190d40f408b6178f98150ba715a3618f0465d82a7ef428faa664c1b8946(
    message_stream: IModelResponseStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47c4d6cf2f6618519902c3e7e8b5ca200c6ea27ef967ef81d537c2d601a4555(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cac852b8ecd970646faefd7e7f5c78bf83418bddc535730146d6ba9907fc3ac1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e00a6ed70830df398a313352c3aa734cc960a79eb64283053ae0ce2fb885b37e(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0bfe00123d03338d92367cb4a0c215e5e30087f33a0f639f19b791714d9624d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad26ac74919683bd213b6b7c419f9948aa9bc38477559c6c6ae0932b7977265(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47cf3fdcbe5ccb300d3cbb6a771bc0d5a9a492eff13540af498af7dc51af0c6e(
    value: typing.Optional[IPCResponseError],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6cfccd993dda54e23963d06288649b6b8b95821a2fff400545a0d111c8dade4(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6904c04f031971514c42cb890a6158dfc42dec3778e4da2b66abdad6d6320137(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e8d00f9cd00687ab975ee8a12462f4808c9da7b9777f99683079ffb1e5520e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6dcdb264b720904f8fcd9fa433897ef3b2ca24edd5612f05268cb41df17833(
    app: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0fd3df91c05e2ff5ab390508306dffbd9f94bc1e370ff9134842fdbe44a251c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9610a90c39cdba00baca8ad2e5bad6527eb3fb1d55f7275ea2498ee8d94e0b37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde4713b77352fa4457cb7fd334b8916978091173e4a083f528dcf1e511383c2(
    value: typing.Optional[Schema],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dae74019e2dcc67378db8e450efc9f233b8147c930b4aedb717cb16bc7149529(
    args: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3134ba045df9b7dd31dee64bd2afc90d2df728641cf5eb61391f1ee3289e65b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d938f80efbeee3b03d22a9d42ea409abc1f9afc91d4a4d4188ed2df32aa1d726(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc57da97f01cb79ce3dbafffc17d8568b2fd74712c6149b60f108707f08d7f68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff37f4f04c9c5488623679f2262e1f67a7cc0a4c61c541b3207799db51bbba24(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c8e7f74423e73a60bef544b22cff2196848b539fea2c0780ca8b1948f35e099(
    args: typing.Any,
    invoker: ITriggerInvoker,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb45739514651aaeafcd9ae6e456d9e2eb7b1925a7a885e80598bf52fb4fc77(
    outcome: IOutcome,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2edbb9866ea0992dac34bbaad4ef3ea74acd211e8e7a1b129ca2abc7b5f072b(
    args: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e2ff7e76bf4f56a2212ad1e2f2468cad3086373ed9420564964da6369b7ecb(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__218f8469c3be1d700c0181c0a20bd6c0ccdf6282e69926295a2a1ffcea919fdb(
    stream: IModelResponseStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf7bdb8585658c1c746590c8cefebf138f2edc15ed6003d9f4a9c8a9614aacef(
    prompt: typing.Sequence[typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce6e38eb3d3c5892fc5c36ee215dee558abe274965a9053f11181e438aa84a64(
    *,
    type_name: builtins.str,
    file: typing.Optional[builtins.str] = None,
    file_data: typing.Optional[typing.Union[FileAttachment, typing.Dict[builtins.str, typing.Any]]] = None,
    image: typing.Optional[builtins.str] = None,
    text: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c37db4d50d0702158938c6db914cbd3af7ae1d5002a4c02c2627e14ba07e725(
    *,
    cached_tokens: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__657743938d459287068308a40aad8943bac32cdbfe386c556d1939e937695a63(
    identifier: builtins.str,
    api_key: ISecret,
    configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b30701319b1c0c5c1c04ccf40e9586ba0cbaa596c04bdca1a59b9e2963f86535(
    *,
    content: typing.Union[builtins.str, typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]]]],
    role: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ebf203d1571bf36977de29383392461c96d558566559a744bfb6b33575fde2(
    *,
    delta: builtins.str,
    output_type: builtins.str,
    sequence_number: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__109d6d097415cd9843b0740082bc89e3af273ab1f914ae31632c2d8cb02347f8(
    *,
    data: typing.Union[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]]]],
    event_name: builtins.str,
    model_instance: typing.Optional[IModel] = None,
    thread_id: typing.Optional[builtins.str] = None,
    usage: typing.Optional[typing.Union[Usage, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c54b2668f4557f0584f65b073361f537a3099cafb0e3e975128080d63a876ad(
    *,
    type_name: builtins.str,
    output_text: typing.Optional[typing.Union[ModelTextOutput, typing.Dict[builtins.str, typing.Any]]] = None,
    output_text_delta: typing.Optional[typing.Union[ModelDeltaOutput, typing.Dict[builtins.str, typing.Any]]] = None,
    requested: typing.Any = None,
    thread_id: typing.Optional[builtins.str] = None,
    tool_call: typing.Optional[typing.Union[ModelToolOutput, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__393dc99748ce602c129bc849b3af84e539b3582bdee11093fb346e0f4d89c7ca(
    *,
    done: builtins.bool,
    value: typing.Optional[typing.Union[ModelResponse, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ecbff96a5661f49f0150361a3ffaa42211ecc8b384ba31880b08a0af8aa8fe(
    *,
    output_type: builtins.str,
    text: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f800bf7fa9ac5c8fcc27fb7b41181d58eec75bccfa7714363f6fcac74ffa5582(
    *,
    arguments: typing.Mapping[builtins.str, typing.Any],
    call_id: builtins.str,
    name: builtins.str,
    output_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331df68d79b2d604251f1008f76d8216ba94333ca3b50cdc1bdab02485bdcdcc(
    outcomes: typing.Sequence[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__598b522f067c9ba908694284b1a33d556dea82c28cb457a0893689b6a317270a(
    *outcomes: IOutcome,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3dbbdbae34fe5c4328e7f07ec5d5070f005978e7d666f836db6cf776d9496a9(
    request: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b042def1a191b2e91def0b062b7e9b29315a532c75421aa20a28ccf8ed60433d(
    message_stream: IModelResponseStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c175767976a8d29950732aaace9fd59145dcc5354ec2395d04d4e499debdffd4(
    *,
    reasoning_tokens: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__337efa37832574be0a930ba07860f808daff0dd38ff876af83acdceae521da21(
    description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56946bef7594a7a59a171969b0175368edb02969935a81a7e00eeb7a7c460e60(
    description: builtins.str,
    enum_values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99c575dc2bf0e46be85e377f2eae4d0c3db9c7b83a978b5ec60ac8d13dc2517(
    description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec81e5158cef1e29b2d84cd99ca741cc93d8fb92b1acc75436519e3e9e2dd73(
    properties: typing.Mapping[builtins.str, ToolArgBuilder],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e762563132c59d170d9506afea7380ed3b7994ca53a51560066a4a450b033cca(
    description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2437b3aa89a027644df9310c8729ef07d53b6af01dc5327ba86d172b163772b(
    env_var_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743f4c3e2ca189338dab8fe52db0739a5dc03deeda7f778525f47b74d895d927(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__241e5fe2d5635c23f63b68933e24dc247545f3c5a32e6287b6dd7589aff6865b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e4c53989901d0db5847a7331c18063736cafe25e10dd820001512d6321c8a25(
    *,
    content_type: builtins.str,
    headers: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
    host: builtins.str,
    method: builtins.str,
    path: builtins.str,
    proto: builtins.str,
    query: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
    remote_addr: builtins.str,
    timestamp: builtins.str,
    body: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2934629c2c7c1cf8c4785cc747882d6fdf2ba9b87a17d9cc5abd98edeaa7f020(
    request: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccab3bbdeba137213879e53553cfb63633ea0532f887d6aee8c69e5e0f801d73(
    message_stream: IModelResponseStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118a405d22ce0f329d0c754a65e2dba723eccae601c98ef1274c1226d2e656e0(
    app: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c465a26a01e4d43a35965d9ee77ffcb88c791c0fa8062aa1c3f4b861e53238(
    request: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6086ef18de2713f1fa28ad9d6c41768205de3085d67df665c2dc9a710171f38a(
    message_stream: IModelResponseStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f41336a4bb494a65c8d528170cdcac4f05c0dcc665485171121f3cb0841b6555(
    *,
    arg_type: builtins.str,
    description: builtins.str,
    required: builtins.bool,
    default_value: typing.Any = None,
    enum_values: typing.Optional[typing.Sequence[builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c98ca3ddf4b0c4129b298763d1682fbb70e2e6262acf5aa904a8cce74b6b7f1(
    arg_type: builtins.str,
    description: builtins.str,
    required: builtins.bool,
    default_value: typing.Any = None,
    enum_values: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02cc88fbf77ef89a25714c7df17626d7770131b8e93b08511ebd5eac7023bd7b(
    default_value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77dc06e59f474d15e254bb52b0b8280d4f126df3f70beebff711224088e10443(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__223fa643d31a84059e93a1975ec7653e74cd3d6f844d52a3e3438d24eec185f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8689cc83c8cc51b6578926a75b25e451bc7a70d90e040252d09b93d13043dde9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bbe183442610cb90c67a7b6c863fc4f25a80dca6d77b1fe96aee423a47bf48f(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40f14e0d1265b816872562f3db5d1d489e92ed9497e3f07978e2812938d172de(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b06cb7c0c8ed9b5a89f4ac05fe513ec187bb25c73068fdbb1d66d69c5f56cf8(
    tool: ITool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c15c77c5fb27e5906320c6e31991181c025de9f1555f4db2f3745fb02461b8(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    tools: typing.Optional[typing.Sequence[ITool]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17db2b7203ff1eaa3855703200b93e2aee61ae9f9eb8cea8d3e52306ff2d8b58(
    *,
    input: typing.Sequence[typing.Union[InputContent, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d24de8f601f1c379d26db5ebe48f48ba5dc5abed10b1441c4faee68c2035a9eb(
    *,
    input_tokens: jsii.Number,
    input_tokens_details: typing.Union[InputTokensDetails, typing.Dict[builtins.str, typing.Any]],
    output_tokens: jsii.Number,
    output_tokens_details: typing.Union[OutputTokensDetails, typing.Dict[builtins.str, typing.Any]],
    total_tokens: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a780658982bd5d1f55e11fc56e862fea30e03665792aaab265d749d583fbda17(
    agent: Agent,
    control_id: builtins.str,
    writer: typing.Optional[IAgentStreamerWriter] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b617812079844c0447bec9a50b46ab48a3ff26e6568affb34fe2994d43bd8ab(
    model: IModel,
    *,
    data: typing.Union[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]], typing.Sequence[typing.Union[ModelResponseData, typing.Dict[builtins.str, typing.Any]]]],
    event_name: builtins.str,
    model_instance: typing.Optional[IModel] = None,
    thread_id: typing.Optional[builtins.str] = None,
    usage: typing.Optional[typing.Union[Usage, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69c4f6318d18b1e977da3ef51f3b9af27d73469e46aa556ea686ae3f36405a01(
    trigger_type: builtins.str,
    config: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0460df3be8bc538f91d112e240db7568e5b3d3966b63378cd56cc592cab951a5(
    args: typing.Any,
    invoker: ITriggerInvoker,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfbb0dd47e0631db7f92e7ce94e70a889b2e5d86f362abcea5831681f3b46f37(
    outcome: IOutcome,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3acdf7981e6153485061b7dd1a4923908be61b4d27808083e8feaa1187a38b9d(
    _: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0731fe7110cc1750189e0b484b0b795c75c45539bf5cbdb618f4551731f1ac19(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9431eaf07533872c8ce0c381fd73c45ae8ce9bf29b333d7c2e5ef9e7fc807e7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cec5b169a731613f477373f14eb05a5003c1ade1162a97a21cac65d0f2e19c2(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccf6278f3562d7eccc209e87ba94ee9b0be3ad48fa162d720d80886dd6b36542(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b96315ac801eb7de8b68f35fbec17b578bb0ede23311b39e3f27c08601c0d35(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4aeffa2e17eb557454896a5f34d88a69e6fc6848ea3f5815fc65b22c77a675c(
    args: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4fd64b2be233cee8fa53ee91cd845e023db430682dc5b33ded79d9325b25bc1(
    _: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50dee7e2c033feea222996f74baf3b87256b409b4975193a1b848683291f8864(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77d3494dba54add6254b36be0222ee5b094a3c391b3c8db59ae732586a18cbf(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc668fd428f011951dda414673ee6c295893590ae107ca4e03b411b4749f135(
    env_var_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd1f615c38c637344765af93fb3efe0fc6590599dcef067eb99953f9c2df1d6(
    args: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf8fdf30315ae18ef201cfcc892f2d043338174d93e6f0d6e6f8169bce4da96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca934182ee092baa0a7df9356d4366e8ab836dacb02ef5fda09aa7e9cf48f6d8(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c1a949ace1c3265367b3fd4ae539d8bde8097a12ff708d0ea375676e13d504(
    expression: builtins.str,
    timezone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c779aee66496c0494c7fb04f76fea9fa7cc2c0fbb87ea9afc080c8f6d3140872(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1875e8f138c3e91e337a0ddb269b9cf391e706bb1575836cc4ad5109de8d268a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11c22831d95c2b0dc4c8784a0be7ea2ebd7131ba74b1cdc9c58625ba45a85595(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322868d921ba17e7302996e348bf5124bd4e777808b91f2d1f351c5a58fe0d35(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db5c6b3801023a3beddc82a4e106fefbc4fd9b8c7d6c9ed34af57b6929f7f9d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80180bc210ca4651ac4a33c6d4c8eef0b95793fcfe80fbadcc175bce68f38702(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e829c4357695b945edd9de3c22fd6bc66b0560de5c0152b7497d44104875165(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c04ed9f932e4ea690e653fb9c5becc1d7785968ded123fbaff6a0c2172df492(
    _: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f722247541d2a4dee16b3d314647938f2a8984c337a09d02dee6c25858855c0(
    on_trigger: IRateTriggerOnTrigger,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78bfccbd1a3f1ccbe5fb53092d0fcc5bf7386096bdabbba6adf3c4d0aadb3d8c(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc520d78b3b42e47e38a737482fd2144e377da18d6b3bf66d3cbb5464b2d107c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c24fc0088fcc90db55b7a025b3041bf7b4b13a1dcb77acba8e4c0938c8803879(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a10624edec3cdb1b33d3c494fd5ef6bb901feed8f69d7f9f3304039ee65b2232(
    raw_args: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ff5c668bcefd2b18cbbe03a38c3b095b5793c7204f0853a0552228673aa0e7(
    raw_args: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e8fd5cca79988489e2997902e7b263d688282e0d84c36aa6f1eabe8e1248074(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d920fae9073c220b4f180598c9916ed9fa80978689ff64bc2d8239b6f5aa17a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77a7ac81bb04ddbda4879fffdad73a5435d8b8239902789e347a76bc78dcd0a(
    value: typing.Optional[IOutcome],
) -> None:
    """Type checking stubs"""
    pass

for cls in [IAgentStreamerWriter, IApiAuthenticator, IModel, IModelFactory, IModelFactoryProps, IModelResponseStream, IModelStreamer, IOutcome, IPCRequest, IPCResponse, IPCResponseError, IRateTriggerOnTrigger, ISecret, IServer, ITool, ITrigger, ITriggerInvoker]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
