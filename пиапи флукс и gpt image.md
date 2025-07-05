GPT-4o Image Generation API
Use Cases
gpt-4o native image generation for text-to-image, image-to-image and conversational-image-editing!!
Far more advanced text rendering than Midjourney or Dalle-3
Two Image Generation Models That We Provide
Model Name	gpt-4o-image	gpt-image-1
API Type	This is a reverse engineered version of ChatGPT image generation feature. It uses LLM API	This is a relayed version of openai gpt-image-1, it uses Images API and just alter the domain name and auth key
Stream Mode	Can only be used in stream mode	Can only be used in stream mode
Pricing	• $0.02 per successful generation
• $0 for 4xx or 5xx errors
• $0.00066 if response contains no image	Low Quality:
• 1024×1024: $0.011
• 1024×1536: $0.016
• 1536×1024: $0.016
Medium Quality:
• 1024×1024: $0.042
• 1024×1536: $0.063
• 1536×1024: $0.063
High Quality:
• 1024×1024: $0.167
• 1024×1536: $0.25
• 1536×1024: $0.25
Implementation	Stream handling required and read below for code examples	Stream handling required, with altered domain name and keys
Notes	No image response may indicate content policy violation or downgrade to DALLE-3	Refer to OpenAI official pricing for complete details
Important Notes
For gpt-4o-image: Image generation failures that return 4xx or 5xx errors are not charged
For gpt-image-1: Implementation follows the same pattern as the standard OpenAI Images API with modified domain and auth headers
Request Examples For gpt-4o-image Model
Here are the examples for gpt-4o-image model, if you are looking for examples around gpt-image-1 model, go to openai offical guid Images API
Simple Text to Image
curl --location 'https://api.piapi.ai/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your-api-key}' \
--data '{
    "model": "gpt-4o-image",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "draw a cyberpunk city"
                }
            ]
        }
    ],
    "stream": true
}'
Simple Image to Image
curl --location 'https://api.piapi.ai/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your-api-key}' \
--data '{
    "model": "gpt-4o-image",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://images.ctfassets.net/kftzwdyauwt9/21orfxKx8HXXGKH8cTOq60/1eb34535ddce9c9e91fab0fad77bc158/minnias_cat_input.png?w=640&q=90&fm=webp"
                    }
                },
                {
                    "type": "text",
                    "text": "Give this cat a detective hat and a monocle"
                }
            ]
        }
    ],
    "stream": true
}'
Multiple Images Input
curl --location 'https://api.piapi.ai/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your-api-key}' \
--data '{
    "model": "gpt-4o-image",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://img.moegirl.org.cn/common/thumb/5/53/Rei_Ayanami.jpg/280px-Rei_Ayanami.jpg"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://moegirl.uk/images/e/ef/OP_C057_asuka.jpg"
                    }
                },
                {
                    "type": "text",
                    "text": "merge two image"
                }
            ]
        }
    ],
    "stream": true
}'
Multiple Rounds Conversation
Different from legacy gpt-4o-image-preview, gpt-4o-image does not have multi rounds feature. It's a WIP feature for gpt-4o-image.




# Flux with LoRA and Controlnet

This service is provided by [PiAPI](https://piapi.ai) in collaboration with Qubico's specialized inference hardware, designed to optimize LoRA (Low-Rank Adaptation) and ControlNet functionalities for advanced model control in various Flux tasks.

## Flux API (Task Creation with LoRA and ControlNet)

### Model, Task Type and LoRA Numbers 
| **Model Name**              | **Task Type**                                      | **LoRA Capacity**      | **Controlnet Capacity**                                                                                           |
|----------------------------------|------------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------|
|Qubico/flux1-dev-advanced|txt2img-lora|1|0|
|Qubico/flux1-dev-advanced|img2img-lora|1|0|
|Qubico/flux1-dev-advanced|controlnet-lora|0 or 1|1|
|Qubico/flux1-dev-advanced|contact us if you need a complex workflow customization|>1|>1|

**Note: `Qubico/flux1-dev-advanced` is the only model that supports LoRA and controlnet in PiAPI's [Flux API](https://piapi.ai/docs/flux-api/text-to-image).** You can explore [Available LoRA and Controlnet](https://piapi.ai/docs/available-lora-and-controlnet) to find out what LoRA or Controlnet model that best fit your need.

### Example:  Request Body of Text-to-Image Task with ControlNet and LoRA
```json
{
  "model": "Qubico/flux1-dev-advanced",
  "task_type": "controlnet-lora",
  "input": {
    "prompt": "spiderman",
    "control_net_settings": [
      {
        "control_type": "depth",
        "control_image": "https://example.com/control_image2.png"
      }
    ],
    "lora_settings": [
      {
        "lora_type": "mjv6"
      }
    ]
  },
  "config": {
    "webhook_config": {
      "endpoint": "https://webhook.site/d35ab4aa-95f9-4855-af82-32fbfbb67063",
      "secret": ""
    }
  }
}
```

# How To Avoid Timeouts in Completion API

We use CloudFlare as our CDN provider and API gateway, which enforces a default 120-second timeout for all requests. As a result, when using the `non-streaming` mode in the text completion API, the process may exceed this time limit. To prevent time-out errors and avoid wasting tokens, you can try one of the following workarounds:

## 1. Enable Stream Mode

Include `stream: true` in the request payload as shown in [LLM API | Basic Completions](/docs/llm-api/completions). This allows you to receive partial results as soon as the connection with the server is established, effectively bypassing the time-out issue.

## 2. Use the Alternative Domain `proxy.piapi.ai`

This endpoint does not use CloudFlare, providing longer time-out limits. However, it may introduce slightly higher latency.

# Use Cases for GPT-4o Image API 

We are pleased to announce the release of the GPT-4o image API, now available for PiAPI user experimentation. This article explores the model's image-generation capabilities through practical use cases, demonstrating its potential to transform creative artworks.

### Use Cases

| Name | Prompt | Reference Image|Output|
| --- | ------- |----------|------|
| Stitch Wool Style | Generate an IP image of a blushing bird based on the example illustration, with a wool felt texture and embroidery style, against a plain beige background. The image should feature soft, diffused lighting, with a clean, aesthetically pleasing, and bright visual effect. | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353874/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353875/image-preview)|
| 3D Model | Convert the main subject in the image into a 3D texture with 3D rendering, a creamy material, and a plain beige background. | ![image.png](https://i.ibb.co/Jj6zB0QQ/We-Chata81cf16c72dbb3b45a0cae4d670882bb.jpg) | ![image.png](https://i.ibb.co/PZ18M6zs/gje-VJw-Ntc3fmt-Bbb-DYXl-SK2-KDGHPAQ.png)|
| Brand Capsule | Create a 1:1 image featuring a tall, realistic, and luxurious-looking capsule floating horizontally. The left half is labeled with the text PiAPI and a combined logo as shown in the reference, using the specified blue color scheme. The right half is transparent, filled with intricate circuit patterns. The background is a solid beige color. | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353885/image-preview) | ![image.png](https://i.ibb.co/GvC9Hpgr/We-Chat42ef48a8d5eed1cd70c2750b81cd5d60.jpg)|
| Clay Model | Transform a flat vector of image into a 3D Play-Doh sculpture with ahandmade clay texture, using the original colors and shape. Light solid beige gray background, studio lighting. | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353887/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353886/image-preview)|
| Poster Generation|Render the main subject in the style of the reference poster https://wx2.sinaimg.cn/mw690/005I0DLKgy1i0kx7l49a2j30u0143af5.jpg style, creating an evenly proportioned poster design with PiAPI as the central visual motif.The aspect ratio is 4:5. | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353888/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353889/image-preview)|
| 3D Wool-texture Model|Render the main subject in 3D wool felt texture with soft material details, against a solid light beige background. | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353890/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353891/image-preview)|
| Sticker Generation|Transform all food elements in the photo into individual stickers, placed on a solid beige background.  | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353892/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353893/image-preview)|
| Gihibli Style|Generate the image into ghibli style | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353897/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353898/image-preview)|
| Four-panel Comic|Create a four-panel comic strip based on the image, illustrating the process of making the food shown.  | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353894/image-preview) | ![image.png](https://api.apidog.com/api/v1/projects/675356/resources/353896/image-preview)|

### Join Our Discord
Through the showcased examples, we aim to help you fully leverage the creative potential of the GPT-4o image API to produce exceptional work. We warmly welcome you to share your creations in our Discord community and connect with fellow creators!






# LLM API | Basic Completions

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /v1/chat/completions:
    post:
      summary: LLM API | Basic Completions
      deprecated: false
      description: "\n:::info\n<br>\n#### Discount\n[PiAPI](https://piapi.ai) also provides different LLM API at cost effective pricing, sometimes at **25%~75%** of their official pricing. \n<br>\n#### Availability\nGiven the steep discount, we **sometimes face availability issues** thus we always recommend developers **to always have another back up API source ready** - take advantage of our low pricing when you can, and when availability becomes a problem switch to a higher cost solution to maintain overall system up-time. \n<br>\n\n:::\n<br>\n\n\n\nmodel name | pricing | Notes\n---------|----------|---------\n gpt-4o-mini | input 1M tokens = \\$0.1125 <br> output 1M tokens = $0.45 | 75% of OpenAI's official pricing \n gpt-4o\t| input 1M tokens = \\$1.875 <br>output 1M tokens = $7.5<br>Only for Creator Plan or Above | 75% of OpenAI's official pricing, as the original OpenAI's API model gpt-4o.\n gpt-4.1 and gpt-4.1-mini and gpt-4.1 nano | 75% of OpenAI's official pricing, as the original OpenAI's API | 75% of OpenAI's official pricing, as the original OpenAI's API\nclaude-3-7-sonnet-20250219| input 1M tokens = \\$2.25<br>output 1M tokens = \\$11.25<br>Only for Creator Plan or Above | 75% of Anthropic's official pricing\nclaude-sonnet-4-20250514| input 1M tokens = \\$2.25<br>output 1M tokens = \\$11.25<br>Only for Creator Plan or Above | 75% of Anthropic's official pricing\ngpt-4o-image|$0.02 per request| see [4o image generation api](/docs/llm-api/gpt-4o-image-generation-api)\ngpt-image-1|same as openai official| see [openai-official-pricing](https://platform.openai.com/docs/pricing)\n\n\nNote:\n\n1. OpenAI's input and output tokens, where 1k token roughly equals to 750 words. Thus 1 token roughly equates to 0.75 word.\n2. The definition of minimum charge: if the actual token (input+output) usage for that particular completion is less than that value, we will round it that value.\n\n\n\n"
      operationId: llm-api/completions
      tags:
        - Endpoints/LLM
        - LLM
      parameters:
        - name: Authorization
          in: header
          description: Your API KEY for authorization
          required: true
          example: ''
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - model
                - messages
              properties:
                model:
                  type: string
                  x-stoplight:
                    id: exgi6qe17viq5
                  description: "The name of the model to be used\r\n<br>**How to get Gizmo model name**: Go to ChatGPT official website, explore the GPTs and enter chat with the GPT of your choice, you will see webpage address like https://chatgpt.com/g/g-gFt1ghYJl-logo-creator. Then the model name you should use is gpt-4-gizmo-g-gFt1ghYJl."
                messages:
                  type: array
                  x-stoplight:
                    id: yx7ovi43im8qh
                  description: A list of messages comprising the conversation so far
                  items:
                    type: string
                functions:
                  type: array
                  x-stoplight:
                    id: 11wm2y2n57odr
                  description: A list of functions the model may generate JSON inputs for.
                  items:
                    type: string
                function_call:
                  type: string
                  x-stoplight:
                    id: 5wcce983znoa8
                  description: "Controls how the model calls functions.<br>\r\n\"none\" means the model will not call a function and instead generates a message. <br>\r\n\"auto\" means the model can pick between generating a message or calling a function. <br>\r\nSpecifying a particular function via {name:my_function} forces the model to call that function. <br>\r\n\"none\" is the default when no functions are present. <br>\r\n\"auto\" is the default if functions are present."
                temperature:
                  type: number
                  x-stoplight:
                    id: nuy2vhjekzkcg
                  description: "Defaults to 1. What sampling temperature to use, between 0 and 2. <br>\r\nHigher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic."
                top_p:
                  type: number
                  x-stoplight:
                    id: 1j3wwdrl71iyl
                  description: "Defaults to 1. <br>\r\nAn alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass.<br>\r\nSo 0.1 means only the tokens comprising the top 10% probability mass are considered."
                'n':
                  type: integer
                  x-stoplight:
                    id: i2hv0alwd2f6t
                  description: "Defaults to 1.<br>\r\nHow many chat completion choices to generate for each input message."
                stream:
                  type: boolean
                  x-stoplight:
                    id: afzcwochwehlz
                  description: "Defaults to false. <br>\r\nIf set, partial message deltas will be sent, like in ChatGPT. <br>\r\nTokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data:[none] message"
                "stop\t":
                  type: string
                  x-stoplight:
                    id: er597n85im51c
                  description: "Defaults to null.<br>\r\nUp to 4 sequences where the API will stop generating further tokens."
                  items:
                    type: string
                max_tokens:
                  type: number
                  x-stoplight:
                    id: h0p3gydjn8f3e
                  description: >-
                    Defaults to the maximum number of tokens to generate in the
                    chat completion.
                presence_penalty:
                  type: number
                  x-stoplight:
                    id: h4500xl2gqt12
                  description: "Defaults to 0. <br>\r\nNumber between -2.0 and 2.0. <br>\r\nPositive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.\r\n"
                frequency_penalty:
                  type: number
                  x-stoplight:
                    id: wkpd3c8ef3lff
                  description: "Defaults to 0. <br>\r\nNumber between -2.0 and 2.0. <br> \r\nPositive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.\r\n"
                logit_bias:
                  type: string
                  x-stoplight:
                    id: hl7rf71y3aw2b
                  description: "Defaults to null. Modify the likelihood of specified tokens appearing in the completion.\r\n"
              x-apidog-orders:
                - model
                - messages
                - functions
                - function_call
                - temperature
                - top_p
                - 'n'
                - stream
                - "stop\t"
                - max_tokens
                - presence_penalty
                - frequency_penalty
                - logit_bias
            example: "//Request Example - No Streaming\r\n\r\ncurl https://api.piapi.ai/v1/chat/completions \\\r\n  -H \"Content-Type: application/json\" \\\r\n  -H \"Authorization: Bearer API_KEY\" \\\r\n  -d '{\r\n    \"model\": \"gpt-3.5-turbo\",\r\n    \"messages\": [\r\n     {\r\n        \"role\": \"system\",\r\n        \"content\": \"You are a helpful assistant.\"\r\n      },\r\n      {\r\n        \"role\": \"user\",\r\n        \"content\": \"Hello!\"\r\n      }\r\n    ]\r\n  }'\r\n\r\n\r\n  //Request Example - Streaming\r\n  curl https://api.piapi.ai/v1/chat/completions \\\r\n  -H \"Content-Type: application/json\" \\\r\n  -H \"Authorization: Bearer API_KEY\" \\\r\n  -d '{\r\n    \"model\": \"gpt-3.5-turbo\",\r\n    \"messages\": [\r\n      {\r\n        \"role\": \"system\",\r\n        \"content\": \"You are a helpful assistant.\"\r\n      },\r\n      {\r\n        \"role\": \"user\",\r\n        \"content\": \"Hello!\"\r\n      }\r\n   ],\r\n    \"stream\": true\r\n  }'"
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  object:
                    type: string
                  created:
                    type: integer
                  model:
                    type: string
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        index:
                          type: integer
                        message:
                          type: object
                          properties:
                            role:
                              type: string
                            content:
                              type: string
                          required:
                            - role
                            - content
                          x-apidog-orders:
                            - role
                            - content
                        finish_reason:
                          type: string
                      x-apidog-orders:
                        - index
                        - message
                        - finish_reason
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: integer
                      completion_tokens:
                        type: integer
                      total_tokens:
                        type: integer
                    required:
                      - prompt_tokens
                      - completion_tokens
                      - total_tokens
                    x-apidog-orders:
                      - prompt_tokens
                      - completion_tokens
                      - total_tokens
                required:
                  - id
                  - object
                  - created
                  - model
                  - choices
                  - usage
                x-apidog-orders:
                  - id
                  - object
                  - created
                  - model
                  - choices
                  - usage
              examples:
                '1':
                  summary: Success- No Streaming
                  value:
                    id: chatcmpl-83jZ61GDHtdlsFUzXDbpGeoU193Mj
                    object: chat.completion
                    created: 1695900828
                    model: gpt-3.5-turbo
                    choices:
                      - index: 0
                        message:
                          role: assistant
                          content: Hello! How can I assist you today?
                        finish_reason: stop
                    usage:
                      prompt_tokens: 19
                      completion_tokens: 9
                      total_tokens: 28
                '2':
                  summary: Success-Steaming
                  value: "data: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"role\":\"assistant\",\"content\":\"\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\"Hello\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\"!\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" How\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" can\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" I\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" assist\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" you\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\" today\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{\"content\":\"?\"},\"finish_reason\":null}]}\r\n \r\ndata: {\"id\":\"chatcmpl-83jctesyk8nEkPytXDNLz1oV5dIQK\",\"object\":\"chat.completion.c\r\nhunk\",\"created\":1695901063,\"model\":\"gpt-3.5-turbo-0613\",\"choices\":[{\"index\":0,\"d\r\nelta\":{},\"finish_reason\":\"stop\"}]}\r\n \r\ndata: [DONE]"
          headers: {}
          x-apidog-name: OK
        '400':
          description: "Bad Request - The request format does not meet the requirements.\r\n"
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apidog-orders: []
          headers: {}
          x-apidog-name: Bad Request
        '401':
          description: "Unauthorized - The API key is incorrect\r\n"
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apidog-orders: []
          headers: {}
          x-apidog-name: Unauthorized
        '500':
          description: Internal Server Error - Service is experiencing an error
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apidog-orders: []
          headers: {}
          x-apidog-name: Server Error
      security: []
      x-apidog-folder: Endpoints/LLM
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-10275420-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```

# Get Task

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/task/{task_id}:
    get:
      summary: Get Task
      deprecated: false
      description: ''
      tags:
        - Endpoints/LLM
      parameters:
        - name: task_id
          in: path
          description: ''
          required: true
          schema:
            type: string
        - name: x-api-key
          in: header
          description: Your API key for authorization
          required: true
          example: ''
          schema:
            type: string
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      task_id:
                        type: string
                      model:
                        type: string
                      task_type:
                        type: string
                      status:
                        type: string
                        enum:
                          - Completed
                          - Processing
                          - Pending
                          - Failed
                          - Staged
                        x-apidog-enum:
                          - value: Completed
                            name: ''
                            description: ''
                          - value: Processing
                            name: ''
                            description: >-
                              Means that your jobs is currently being processed.
                              Number of "processing" jobs counts as part of the
                              "concurrent jobs"
                          - value: Pending
                            name: ''
                            description: >-
                              Means that we recognizes the jobs you sent should
                              be processed by MJ/Luma/Suno/Kling/etc but right
                              now none of the  account is available to receive
                              further jobs. During peak loads there can be
                              longer wait time to get your jobs from "pending"
                              to "processing". If reducing waiting time is your
                              primary concern, then a combination of
                              Pay-as-you-go and Host-your-own-account option
                              might suit you better.Number of "pending" jobs
                              counts as part of the "concurrent jobs"
                          - value: Failed
                            name: ''
                            description: Task failed. Check the error message for detail.
                          - value: Staged
                            name: ''
                            description: >-
                              A stage only in Midjourney task . Means that you
                              have exceeded the number of your "concurrent jobs"
                              limit and your jobs are being queuedNumber of
                              "staged" jobs does not count as part of the
                              "concurrent jobs". Also, please note the maximum
                              number of jobs in the "staged" queue is 50. So if
                              your operational needs exceed the 50 jobs limit,
                              then please create your own queuing system logic. 
                        description: >-
                          Hover on the "Completed" option and you coult see the
                          explaintion of all status:
                          completed/processing/pending/failed/staged
                      input:
                        type: object
                        properties: {}
                        x-apidog-orders: []
                        x-apidog-ignore-properties: []
                      output:
                        type: object
                        properties: {}
                        x-apidog-orders: []
                        x-apidog-ignore-properties: []
                      meta:
                        type: object
                        properties:
                          created_at:
                            type: string
                            description: >-
                              The time when the task was submitted to us (staged
                              and/or pending)
                          started_at:
                            type: string
                            description: >-
                              The time when the task started processing. the
                              time from created_at to time of started_at is time
                              the job spent in the "staged“ stage and/or
                              the"pending" stage if there were any.
                          ended_at:
                            type: string
                            description: The time when the task finished processing.
                          usage:
                            type: object
                            properties:
                              type:
                                type: string
                              frozen:
                                type: number
                              consume:
                                type: number
                            x-apidog-orders:
                              - type
                              - frozen
                              - consume
                            required:
                              - type
                              - frozen
                              - consume
                            x-apidog-ignore-properties: []
                          is_using_private_pool:
                            type: boolean
                        x-apidog-orders:
                          - created_at
                          - started_at
                          - ended_at
                          - usage
                          - is_using_private_pool
                        required:
                          - usage
                          - is_using_private_pool
                        x-apidog-ignore-properties: []
                      detail:
                        type: 'null'
                      logs:
                        type: array
                        items:
                          type: object
                          properties: {}
                          x-apidog-orders: []
                          x-apidog-ignore-properties: []
                      error:
                        type: object
                        properties:
                          code:
                            type: integer
                          message:
                            type: string
                        x-apidog-orders:
                          - code
                          - message
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    required:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    x-apidog-ignore-properties: []
                  message:
                    type: string
                    description: >-
                      If you get non-null error message, here are some steps you
                      chould follow:

                      - Check our [common error
                      message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)

                      - Retry for several times

                      - If you have retried for more than 3 times and still not
                      work, file a ticket on Discord and our support will be
                      with you soon.
                x-apidog-orders:
                  - 01J8H2AX3H983HVKWVPNK0803A
                required:
                  - code
                  - data
                  - message
                x-apidog-refs:
                  01J8H2AX3H983HVKWVPNK0803A:
                    $ref: '#/components/schemas/Unified-Task-Response'
                x-apidog-ignore-properties:
                  - code
                  - data
                  - message
              example:
                choices:
                  - finish_reason: stop
                    index: 0
                    logprobs: null
                    message:
                      content: Hello! How can I assist you today?
                      refusal: null
                      role: assistant
                created: 1742390255
                id: chatcmpl-BCnaZUo5Bm2Lh0kMjzea9i8rQiQVb
                model: gpt-4o-mini-2024-07-18
                object: chat.completion
                system_fingerprint: fp_b705f0c291
                usage:
                  completion_tokens: 10
                  completion_tokens_details:
                    accepted_prediction_tokens: 0
                    audio_tokens: 0
                    reasoning_tokens: 0
                    rejected_prediction_tokens: 0
                  prompt_tokens: 19
                  prompt_tokens_details:
                    audio_tokens: 0
                    cached_tokens: 0
                  total_tokens: 29
          headers: {}
          x-apidog-name: Success
      security: []
      x-apidog-folder: Endpoints/LLM
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-14943756-run
components:
  schemas:
    Unified-Task-Response:
      type: object
      properties:
        code:
          type: integer
        data:
          type: object
          properties:
            task_id:
              type: string
            model:
              type: string
            task_type:
              type: string
            status:
              type: string
              enum:
                - Completed
                - Processing
                - Pending
                - Failed
                - Staged
              x-apidog-enum:
                - value: Completed
                  name: ''
                  description: ''
                - value: Processing
                  name: ''
                  description: >-
                    Means that your jobs is currently being processed. Number of
                    "processing" jobs counts as part of the "concurrent jobs"
                - value: Pending
                  name: ''
                  description: >-
                    Means that we recognizes the jobs you sent should be
                    processed by MJ/Luma/Suno/Kling/etc but right now none of
                    the  account is available to receive further jobs. During
                    peak loads there can be longer wait time to get your jobs
                    from "pending" to "processing". If reducing waiting time is
                    your primary concern, then a combination of Pay-as-you-go
                    and Host-your-own-account option might suit you
                    better.Number of "pending" jobs counts as part of the
                    "concurrent jobs"
                - value: Failed
                  name: ''
                  description: Task failed. Check the error message for detail.
                - value: Staged
                  name: ''
                  description: >-
                    A stage only in Midjourney task . Means that you have
                    exceeded the number of your "concurrent jobs" limit and your
                    jobs are being queuedNumber of "staged" jobs does not count
                    as part of the "concurrent jobs". Also, please note the
                    maximum number of jobs in the "staged" queue is 50. So if
                    your operational needs exceed the 50 jobs limit, then please
                    create your own queuing system logic. 
              description: >-
                Hover on the "Completed" option and you coult see the
                explaintion of all status:
                completed/processing/pending/failed/staged
            input:
              type: object
              properties: {}
              x-apidog-orders: []
              x-apidog-ignore-properties: []
            output:
              type: object
              properties: {}
              x-apidog-orders: []
              x-apidog-ignore-properties: []
            meta:
              type: object
              properties:
                created_at:
                  type: string
                  description: >-
                    The time when the task was submitted to us (staged and/or
                    pending)
                started_at:
                  type: string
                  description: >-
                    The time when the task started processing. the time from
                    created_at to time of started_at is time the job spent in
                    the "staged“ stage and/or the"pending" stage if there were
                    any.
                ended_at:
                  type: string
                  description: The time when the task finished processing.
                usage:
                  type: object
                  properties:
                    type:
                      type: string
                    frozen:
                      type: number
                    consume:
                      type: number
                  x-apidog-orders:
                    - type
                    - frozen
                    - consume
                  required:
                    - type
                    - frozen
                    - consume
                  x-apidog-ignore-properties: []
                is_using_private_pool:
                  type: boolean
              x-apidog-orders:
                - created_at
                - started_at
                - ended_at
                - usage
                - is_using_private_pool
              required:
                - usage
                - is_using_private_pool
              x-apidog-ignore-properties: []
            detail:
              type: 'null'
            logs:
              type: array
              items:
                type: object
                properties: {}
                x-apidog-orders: []
                x-apidog-ignore-properties: []
            error:
              type: object
              properties:
                code:
                  type: integer
                message:
                  type: string
              x-apidog-orders:
                - code
                - message
              x-apidog-ignore-properties: []
          x-apidog-orders:
            - task_id
            - model
            - task_type
            - status
            - input
            - output
            - meta
            - detail
            - logs
            - error
          required:
            - task_id
            - model
            - task_type
            - status
            - input
            - output
            - meta
            - detail
            - logs
            - error
          x-apidog-ignore-properties: []
        message:
          type: string
          description: >-
            If you get non-null error message, here are some steps you chould
            follow:

            - Check our [common error
            message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)

            - Retry for several times

            - If you have retried for more than 3 times and still not work, file
            a ticket on Discord and our support will be with you soon.
      x-examples:
        Example 1:
          code: 200
          data:
            task_id: 49638cd2-4689-4f33-9336-164a8f6b1111
            model: Qubico/flux1-dev
            task_type: txt2img
            status: pending
            input:
              prompt: a bear
            output: null
            meta:
              account_id: 0
              account_name: Qubico_test_user
              created_at: '2024-08-16T16:13:21.194049Z'
              started_at: ''
              completed_at: ''
            detail: null
            logs: []
            error:
              code: 0
              message: ''
          message: success
      x-apidog-orders:
        - code
        - data
        - message
      required:
        - code
        - data
        - message
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```








### Request Example Using cURL

```bash
curl --location --request POST 'https://api.piapi.ai/api/v1/task' --header 'X-API-KEY: YOUR_API_KEY' --header 'Content-Type: application/json' --data-raw '{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "controlnet-lora",
    "input": {
        "prompt": "spiderman",
        "control_net_settings": [
            {
                "control_type": "depth",
                "control_image": "https://example.com/control_image1.png"
            }
        ],
        "lora_settings": [
            {
                "lora_type": "mjv6"
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "https://webhook.site/d35ab4aa-95f9-4855-af82-32fbfbb67063",
            "secret": ""
        }
    }
}'
```

### Example: Request Body of Task Creation with LoRA only

Input Example:
```json
{
  "model": "Qubico/flux1-dev-advanced",
  "task_type": "txt2img-lora",
  "input": {
    "prompt": "spiderman",
    "lora_settings": [
      {
        "lora_type": "mjv6"
      }
    ]
  },
  "config": {
    "webhook_config": {
      "endpoint": "https://webhook.site/d35ab4aa-95f9-4855-af82-32fbfbb67063",
      "secret": ""
    }
  }
}
```

### Example: Task Creation with controlnet Canny

```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "controlnet-lora",
    "input": {
        "steps": 28,
        "prompt": "A girl in city, 25 years old, cool, futuristic",
        "negative_prompt": "low quality, ugly, distorted, artefacts",
        "guidance_scale": 2.5,
        "control_net_settings": [
            {
                "control_type": "canny",
                "control_image": "https://i.ibb.co/yX07dwV/Comfy-UI-controlnet.webp",
                "control_strength": 0.45,
                "return_preprocessed_image": true
            }
        ],
        "lora_settings": [
            {
                "lora_type": "graphic-portrait",
                "lora_strength": 1
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "",
            "secret": ""
        }
    }
}
```

| Canny Result 1         | Canny Result 2         |
|------------------|-----------------|
| ![Alt text 1](https://i.ibb.co/fG5C6kz/canny1.png) | ![Alt text 2](https://i.ibb.co/FwQqhmz/canny2.png) |

### Example: Task Creation with controlnet Depth

```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "controlnet-lora",
    "input": {
        "steps": 28,
        "prompt": "A girl in city, 25 years old, cool, futuristic",
        "negative_prompt": "low quality, ugly, distorted, artefacts",
        "guidance_scale": 2.5,
        "control_net_settings": [
            {
                "control_type": "depth",
                "control_image": "https://i.ibb.co/yX07dwV/Comfy-UI-controlnet.webp",
                "control_strength": 0.45,
                "return_preprocessed_image": true
            }
        ],
        "lora_settings": [
            {
                "lora_type": "geometric-woman",
                "lora_strength": 1
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "",
            "secret": ""
        }
    }
}
```

| Depth Result 1         | Depth Result 2         |
|------------------|-----------------|
| ![Alt text 1](https://i.ibb.co/HNSzwWx/depth1.png) | ![Alt text 2](https://i.ibb.co/8Kf1P9P/depth2.png) |

### Example: Task Creation with controlnet SoftEdge

```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "controlnet-lora",
    "input": {
        "steps": 28,
        "prompt": "A girl in city, 25 years old, cool, futuristic",
        "negative_prompt": "low quality, ugly, distorted, artefacts",
        "guidance_scale": 2.5,
        "control_net_settings": [
            {
                "control_type": "soft_edge",
                "control_image": "https://i.ibb.co/yX07dwV/Comfy-UI-controlnet.webp",
                "control_strength": 0.55,
                "return_preprocessed_image": true
            }
        ],
        "lora_settings": [
            {
                "lora_type": "remes-abstract-poster-style",
                "lora_strength": 1
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "https://webhook.site/0edf5555-22ba-4aae-898a-f707440effa4",
            "secret": ""
        }
    }
}
```

| Softedge Result 1         | Softedge Result 2         |
|------------------|-----------------|
| ![Alt text 1](https://i.ibb.co/Pxqm9NM/softedge1.png) | ![Alt text 2](https://i.ibb.co/p3N6ZtF/softedge2.png) |


### Example: Task Creation with controlnet OpenPose
```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "controlnet-lora",
    "input": {
        "steps": 28,
        "prompt": "person enjoying a day at the park, full hd, cinematic",
        "negative_prompt": "low quality, ugly, distorted, artefacts",
        "guidance_scale": 4.0,
        "control_net_settings": [
            {
                "control_type": "openpose",
                "control_image": "https://i.ibb.co/vkCbMZY/3-pose-1024.jpg",
                "control_strength": 0.7,
                "return_preprocessed_image": true
            }
        ],
        "lora_settings": [
            {
                "lora_type": "mjv6",
                "lora_strength": 1
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "https://webhook.site/0edf5555-22ba-4aae-898a-f707440effa4",
            "secret": ""
        }
    }
}
```

| OpenPose Control Image INPUT       | OpenPose Result         |
|------------------|-----------------|
| ![Alt text 1](https://i.ibb.co/WtZ0mcq/pose1.png) | ![Alt text 2](https://i.ibb.co/0FvWxqH/pose2.png) |


# Available LoRA and Controlnet

**This page lists all available LoRA and ControlNet models for [PiAPI's Flux API](https://piapi.ai/flux-api), including examples of their settings and image results.** You can try these models by following our instruction [Flux with LoRA and controlnet](/docs/flux-with-lora-and-controlnet)

## Available LoRA Models

| **LoRA Model Name**              | **Source**                                      | **JSON Setting Structure Example**      | **Example Image**                                                                                           |
|----------------------------------|------------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------|
| Anime                            | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "anime"}`                | ![Anime Example](https://i.ibb.co/rvy8k31/anime.png)                                                      |
| Art                              | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "art"}`                  | ![Art Example](https://i.ibb.co/HYgMHpF/art.png)                                                          |
| Disney                           | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "disney"}`               | ![Disney Example](https://i.ibb.co/cDDG7zn/disney.png)                                                    |
| Furry                            | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "furry"}`                | ![Furry Example](https://i.ibb.co/g4JJbyJ/furry.png)                                                      |
| MJv6                             | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "mjv6"}`                 | ![MJv6 Example](https://i.ibb.co/G7RRqZh/mjv6.png)                                                        |
| Realism                          | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "realism"}`              | ![Realism Example](https://i.ibb.co/YNLwkRj/realism.png)                                                  |
| Scenery                          | https://huggingface.co/XLabs-AI/flux-lora-collection | `{"lora_type": "scenery"}`              | ![Scenery Example](https://i.ibb.co/vxX2fqx/scenery.png)                                                  |
| Collage Artstyle                 | https://civitai.com/models/748468/retro-collage-art  | `{"lora_type": "collage-artstyle"}`     | ![Collage Artstyle Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/14991cfb-04d3-49bb-86a9-1a1b5cb5e16d/original=true,quality=10/1d1ec133-3187-4f2a-9fd1-1a19fa2741f6.jpeg) |
| Creepycute                       | https://civitai.com/models/788990/creepycute        | `{"lora_type": "creepcute"}`            | ![Creepycute Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/f7e9e831-7cc9-4991-b457-9341eb4e0b5a/original=true,quality=10/1.jpeg) |
| Cyberpunk Anime Style            | https://civitai.com/models/128568/cyberpunk-anime-style | `{"lora_type": "cyberpunk-anime-style"}` | ![Cyberpunk Anime Style Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/eec5618a-f36d-4587-8b15-e6a27878aad3/original=true,quality=10/flux_00568_.jpeg) |
| Deco Pulse                       | https://civitai.com/models/720587/decopulse-flux    | `{"lora_type": "deco-pulse"}`           | ![Deco Pulse Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/475aad1a-939e-460d-a1fe-f601fc2088d4/original=true,quality=10/VS12.jpeg) |
| Deep Sea Particle Enhancer       | https://civitai.com/models/15452/paseer-moxin-assist-for-adding-colorful | `{"lora_type": "deep-sea-particle-enhencer"}` | ![Deep Sea Particle Enhancer Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d76cf937-0877-44b2-a7e7-85733d030c18/original=true,quality=10/particle-001.jpeg) |
| Faetastic Details                | https://civitai.com/models/643886/flux-faetastic-details | `{"lora_type": "faetastic-details"}`    | ![Faetastic Details Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5613fa67-ddea-4784-bba5-9468f66e24ee/original=true,quality=10/MarkuryFLUX_00527_.jpeg) |
| Fractal Geometry                 | https://civitai.com/models/269592/fractal-geometry-style-fluxsdxl15 | `{"lora_type": "fractal-geometry"}`     | ![Fractal Geometry Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6e5287e0-c662-4515-b48e-442ce46fdc32/original=true,quality=10/00019-3128378175.jpeg) |
| Galactixy Illustrations Style    | https://civitai.com/models/747833/galactixy-illustrations-style | `{"lora_type": "galactixy-illustrations-style"}` | ![Galactixy Illustrations Style Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/82074182-d56a-4857-b7b6-c02963ab8268/original=true,quality=10/2024-09-14-133324.jpeg) |
| Geometric Woman                  | https://civitai.com/models/103528/geometric-woman | `{"lora_type": "geometric-woman"}`      | ![Geometric Woman Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/de6f6f38-9749-4cd1-8e6f-b40eb754a0e1/original=true,quality=10/flux_00283_.jpeg) |
| Graphic Portrait                 | https://civitai.com/models/170039/graphic-portrait | `{"lora_type": "graphic-portrait"}`     | ![Graphic Portrait Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0f1b2f23-acb6-471d-a4b1-439dbd117560/original=true,quality=10/flux_03654_.jpeg) |
| Mat Miller Art                   | https://civitai.com/models/894974/mat-miller-art-style | `{"lora_type": "mat-miller-art"}`       | ![Mat Miller Art Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/f5ba9cd2-8d76-40aa-b8b3-338cdf208dfa/original=true,quality=10/ComfyUI_00131_.jpeg) |
| Moebius Style                    | https://civitai.com/models/682651/moebius-style-flux | `{"lora_type": "moebius-style"}`        | ![Moebius Style Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/ffebd187-21a0-488b-bb92-70d3bab07d78/original=true,quality=10/PEQ1V9K5V038EDM5DDK8GQR5E0.jpeg) |
| OB3D Isometric 3D Room           | https://civitai.com/models/555323/ob3d-isometric-3d-room-v20 | `{"lora_type": "ob3d-isometric-3d-room"}` | ![OB3D Isometric 3D Room Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/ab78c3ac-5582-4dc2-9e00-715803eb063b/original=true,quality=10/772392869706130877.jpeg) |
| Paper Quilling and Layering Style | https://civitai.com/models/860403/paper-quilling-and-layering-style-flux | `{"lora_type": "paper-quilling-and-layering-style"}` | ![Paper Quilling Example](https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d6167ae2-8d41-40b4-8141-dfc3d5dcd9f1/original=true,quality=10/ComfyUI_00005_.jpeg)


<br/>

## Available ControlNet Models

| **ControlNet Model Name** | **Description** | **JSON Setting Structure Example** | **Example Image Result** |
| ------------------------ | --------------- | ---------------------------------- | ------------------------ |
| Depth                    | ControlNet model for depth map-based control | `{"control_type": "depth", "control_image": "https://example.com/depth_example.png"}` | ![Depth Example](https://i.ibb.co/YZZWSqq/depth.png) |
| Soft Edge                | ControlNet model for soft edge detection and control | `{"control_type": "soft_edge", "control_image": "https://example.com/soft_edge_example.png"}` | ![Soft Edge Example](https://i.ibb.co/MBCSWVZ/soft-edge.png) |
| Canny                    | ControlNet model for Canny edge detection control | `{"control_type": "canny", "control_image": "https://example.com/canny_example.png"}` | ![Canny Example](https://i.ibb.co/MfR9Cg4/canny.png) |

<br/>

## Help Us Grow the List!

We are constantly expanding our available LoRA and ControlNet models. If you have any suggestions or requests for specific models, feel free to join our Discord community(Shortcut to our discord is on the right-top corner) and submit your feature requests. Help us upload more LoRAs and ControlNets to enhance the capabilities of our API!


# Flux API with Redux Variation, Fill, Inpaint and Outpaint

## Flux API (Task Creation with fill or redux)

### Model, Task Type and Usage 
| **Model Name**              | **Task Type**                                      | **Usage**      |                                                                           
|----------------------------------|------------------------------------------------|-----------------------------------------|
|Qubico/flux1-dev-advanced|fill-inpaint|inpaint a masked area of a given image|
|Qubico/flux1-dev-advanced|fill-outpaint|outpaint/pan/expand a given image|
|Qubico/flux1-dev-advanced|redux-variation|remix/variation on a given image|
|Contact Us|contact us if you need a complex workflow customization|-|

**Note: `Qubico/flux1-dev-advanced` is the only model that supports `fill-inpaint`, `fill-outpaint` and `redux-variation` in PiAPI's [Flux API](/docs/flux-api/create-task).** 

### Example:  Request Body of Inpaint Task
```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "fill-inpaint",
    "input": {
        "prompt": "a girl in blue and red skirt",
        "image": "https://i.ibb.co/TH7xMvd/girl-mask.png"//should come with a white pixel masked area 
    },
    "config": {
        "webhook_config": {
            "endpoint": "",
            "secret": ""
        }
    }
}
```

### Example:  Request Body of Outpaint Task
```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "fill-outpaint",
    "input": {
        "prompt": "a girl in a great grass sea",
        "image": "https://i.ibb.co/TH7xMvd/girl-mask.png",
        "custom_settings": [ //the total delta pixel size should be less than 1024*1024
            {
                "setting_type": "outpaint",
                "outpaint_left": 500,
                "outpaint_right": 500,//this result in a 2024x1024 final image
                "outpaint_top": 0,
                "outpaint_bottom": 0
            }
        ]
    },
    "config": {
        "webhook_config": {
            "endpoint": "",
            "secret": ""
        }
    }
}
```

### Example:  Request Body of Variation(remix) Task
```json
{
    "model": "Qubico/flux1-dev-advanced",
    "task_type": "redux-variation",
    "input": {
        "prompt": "a superman",
        "image": "https://i.ibb.co/TH7xMvd/girl-mask.png"
    },
    "config": {
        "webhook_config": {
            "endpoint": "",
            "secret": ""
        }
    }
}
```

# Text to Image

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/task:
    post:
      summary: Text to Image
      deprecated: false
      description: >-
        This is provided as part of the [Flux API](https://piapi.ai/flux-api)
        from PiAPI.  available models: 

        - Qubico/flux1-dev

        - Qubico/flux1-schnell

        - Qubico/flux1-dev-advanced 

        Check [Flux with LoRA and
        Controlnet](/docs/flux-with-lora-and-controlnet) to learn how to send
        Flux with LoRA and Controlnet task.

        Check [Flux with Redux and
        Fill](/docs/flux-redux-fill-variation-inpaint-outpaint) to learn how to
        send Flux with variation, inpaint and out paint task.


        Below is an example of a ***text-to-image*** request and response.
      operationId: flux-api/text-to-image
      tags:
        - Endpoints/Flux/Create Task
        - FLUX
      parameters:
        - name: X-API-Key
          in: header
          description: Your API KEY used for request authorization
          required: true
          example: ''
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  description: >-
                    the model name, can be `Qubico/flux1-dev` or
                    `Qubico/flux1-schnell` or `Qubico/flux1-dev-advanced`
                  enum:
                    - Qubico/flux1-schnell
                    - Qubico/flux1-dev
                    - Qubico/flux1-dev-advanced
                  x-apidog-enum:
                    - value: Qubico/flux1-schnell
                      name: ''
                      description: ''
                    - value: Qubico/flux1-dev
                      name: ''
                      description: ''
                    - value: Qubico/flux1-dev-advanced
                      name: ''
                      description: ''
                task_type:
                  type: string
                  enum:
                    - txt2img
                    - img2img
                    - txt2img-lora
                    - img2img-lora
                    - fill-inpaint
                    - fill-outpaint
                    - redux-variation
                    - controlnet-lora
                  x-apidog-enum:
                    - value: txt2img
                      name: ''
                      description: ''
                    - value: img2img
                      name: ''
                      description: ''
                    - value: txt2img-lora
                      name: ''
                      description: ''
                    - value: img2img-lora
                      name: ''
                      description: ''
                    - value: fill-inpaint
                      name: ''
                      description: ''
                    - value: fill-outpaint
                      name: ''
                      description: ''
                    - value: redux-variation
                      name: ''
                      description: ''
                    - value: controlnet-lora
                      name: ''
                      description: ''
                input:
                  type: object
                  properties:
                    prompt:
                      type: string
                    negative_prompt:
                      type: string
                    denoise:
                      type: number
                      default: 0.7
                      minimum: 0
                      maximum: 1
                      exclusiveMinimum: true
                    guidance_scale:
                      type: number
                      description: >-
                        Guidance scale for image generation. High guidance
                        scales improve prompt adherence at the cost of reduced
                        realism.
                      minimum: 1.5
                      maximum: 5
                    width:
                      type: integer
                      description: >-
                        can be used in txt2img ONLY, width*height cannot exceed
                        1048576
                    height:
                      type: integer
                      description: >-
                        can be used in txt2img ONLY, width*height cannot exceed
                        1048576
                    batch_size:
                      type: number
                      default: 1
                      minimum: 1
                      maximum: 4
                      description: >-
                        number of images, only works for schnell at the moment.
                        Price will be 

                        batch_size * (price for one generation)
                    lora_settings:
                      type: array
                      items:
                        type: object
                        properties:
                          lora_type:
                            type: string
                            description: >-
                              name of the lora model, check [Available LoRA and
                              Controlnet](/docs/available-lora-and-controlnet)
                          lora_image:
                            type: string
                            description: optional
                        x-apidog-orders:
                          - lora_type
                          - lora_image
                        x-apidog-ignore-properties: []
                      description: >-
                        Check [Flux with LoRA and
                        Controlnet](/docs/flux-with-lora-and-controlnet)
                    control_net_settings:
                      type: array
                      items:
                        type: object
                        properties:
                          control_type:
                            type: string
                            description: >-
                              name of the controlnet model, check [Available
                              LoRA and
                              Controlnet](/docs/available-lora-and-controlnet)
                          control_image:
                            type: string
                            description: image url of the control image
                        x-apidog-orders:
                          - control_type
                          - control_image
                        required:
                          - control_type
                        x-apidog-ignore-properties: []
                      description: >-
                        Check [Flux with LoRA and
                        Controlnet](/docs/flux-with-lora-and-controlnet)
                  x-apidog-orders:
                    - prompt
                    - negative_prompt
                    - denoise
                    - guidance_scale
                    - width
                    - height
                    - batch_size
                    - lora_settings
                    - control_net_settings
                  required:
                    - prompt
                  description: |
                    the input param of the flux task
                  x-apidog-ignore-properties: []
                config:
                  type: object
                  properties:
                    webhook_config:
                      type: object
                      properties:
                        endpoint:
                          type: string
                        secret:
                          type: string
                      x-apidog-orders:
                        - endpoint
                        - secret
                      description: >-
                        Webhook provides timely task notifications. Check [PiAPI
                        webhook](/docs/unified-webhook) for detail.
                      x-apidog-ignore-properties: []
                    service_mode:
                      type: string
                      description: >
                        This allows users to choose whether this specific task
                        will get processed under PAYG or HYA mode. If
                        unspecified, then this task will get processed under
                        whatever mode (PAYG or HYA)
                         the user chose on the workspace setting of your account.
                        - `public` means this task will be processed under PAYG
                        mode.

                        - `private` means this task will be processed under HYA
                        mode.
                      enum:
                        - public
                        - private
                      x-apidog-enum:
                        - value: public
                          name: ''
                          description: means this task will be processed under PAYG mode.
                        - value: private
                          name: ''
                          description: >-
                            means this task will be processed under HYA
                            modesetting of your account.
                  x-apidog-orders:
                    - webhook_config
                    - service_mode
                  x-apidog-ignore-properties: []
              x-apidog-refs:
                01J8PNX50491VGB1V6ZTHX081W:
                  $ref: '#/components/schemas/config'
              x-apidog-orders:
                - model
                - task_type
                - input
                - 01J8PNX50491VGB1V6ZTHX081W
              required:
                - task_type
                - input
                - model
              x-apidog-ignore-properties:
                - config
            example:
              model: Qubico/flux1-dev
              task_type: txt2img
              input:
                prompt: a little cat
                width: 1024
                height: 1024
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      task_id:
                        type: string
                      model:
                        type: string
                      task_type:
                        type: string
                      status:
                        type: string
                        enum:
                          - Completed
                          - Processing
                          - Pending
                          - Failed
                          - Staged
                        x-apidog-enum:
                          - value: Completed
                            name: ''
                            description: ''
                          - value: Processing
                            name: ''
                            description: >-
                              Means that your jobs is currently being processed.
                              Number of "processing" jobs counts as part of the
                              "concurrent jobs"
                          - value: Pending
                            name: ''
                            description: >-
                              Means that we recognizes the jobs you sent should
                              be processed by MJ/Luma/Suno/Kling/etc but right
                              now none of the  account is available to receive
                              further jobs. During peak loads there can be
                              longer wait time to get your jobs from "pending"
                              to "processing". If reducing waiting time is your
                              primary concern, then a combination of
                              Pay-as-you-go and Host-your-own-account option
                              might suit you better.Number of "pending" jobs
                              counts as part of the "concurrent jobs"
                          - value: Failed
                            name: ''
                            description: Task failed. Check the error message for detail.
                          - value: Staged
                            name: ''
                            description: >-
                              A stage only in Midjourney task . Means that you
                              have exceeded the number of your "concurrent jobs"
                              limit and your jobs are being queuedNumber of
                              "staged" jobs does not count as part of the
                              "concurrent jobs". Also, please note the maximum
                              number of jobs in the "staged" queue is 50. So if
                              your operational needs exceed the 50 jobs limit,
                              then please create your own queuing system logic. 
                        description: >-
                          Hover on the "Completed" option and you coult see the
                          explaintion of all status:
                          completed/processing/pending/failed/staged
                      input:
                        type: object
                        properties: {}
                        x-apidog-orders: []
                        x-apidog-ignore-properties: []
                      output:
                        type: object
                        properties:
                          image_url:
                            type: string
                            description: if the result contains only one image
                          image_urls:
                            type: array
                            items:
                              type: string
                            description: if the result contains multiple images
                        x-apidog-orders:
                          - image_url
                          - image_urls
                        x-apidog-ignore-properties: []
                      meta:
                        type: object
                        properties:
                          created_at:
                            type: string
                            description: >-
                              The time when the task was submitted to us (staged
                              and/or pending)
                          started_at:
                            type: string
                            description: >-
                              The time when the task started processing. the
                              time from created_at to time of started_at is time
                              the job spent in the "staged“ stage and/or
                              the"pending" stage if there were any.
                          ended_at:
                            type: string
                            description: The time when the task finished processing.
                          usage:
                            type: object
                            properties:
                              type:
                                type: string
                              frozen:
                                type: number
                              consume:
                                type: number
                            x-apidog-orders:
                              - type
                              - frozen
                              - consume
                            required:
                              - type
                              - frozen
                              - consume
                            x-apidog-ignore-properties: []
                          is_using_private_pool:
                            type: boolean
                        x-apidog-orders:
                          - created_at
                          - started_at
                          - ended_at
                          - usage
                          - is_using_private_pool
                        required:
                          - usage
                          - is_using_private_pool
                        x-apidog-ignore-properties: []
                      detail:
                        type: 'null'
                      logs:
                        type: array
                        items:
                          type: object
                          properties: {}
                          x-apidog-orders: []
                          x-apidog-ignore-properties: []
                      error:
                        type: object
                        properties:
                          code:
                            type: integer
                          message:
                            type: string
                        x-apidog-orders:
                          - code
                          - message
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    required:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    x-apidog-ignore-properties: []
                  message:
                    type: string
                    description: >-
                      If you get non-null error message, here are some steps you
                      chould follow:

                      - Check our [common error
                      message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)

                      - Retry for several times

                      - If you have retried for more than 3 times and still not
                      work, file a ticket on Discord and our support will be
                      with you soon.
                x-apidog-refs: {}
                x-apidog-orders:
                  - code
                  - data
                  - message
                required:
                  - code
                  - data
                  - message
                x-apidog-ignore-properties: []
              example: "{\r\n    \"code\": 200,\r\n    \"message\": \"success\",\r\n    \"data\": {\r\n        \"task_id\": \"0f647527-12bd-48b1-b813-111111111\",\r\n        \"model\": \"Qubico/flux1-dev\", \r\n        \"task_type\": \"txt2img\",\r\n        \"status\": \"\", // pending/processing/failed/completed\r\n        \"input\": {}, \r\n        \"output\": {}, \r\n        \"meta\": { \r\n        },\r\n        \"logs\": [],\r\n        \"error\": {\r\n            \"code\": 1100,\r\n            \"message\": \"\"\r\n        } \r\n    }\r\n}"
          headers: {}
          x-apidog-name: Success
      security: []
      x-apidog-folder: Endpoints/Flux/Create Task
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-10275644-run
components:
  schemas:
    config:
      type: object
      properties:
        config:
          type: object
          properties:
            webhook_config:
              type: object
              properties:
                endpoint:
                  type: string
                secret:
                  type: string
              x-apidog-orders:
                - endpoint
                - secret
              description: >-
                Webhook provides timely task notifications. Check [PiAPI
                webhook](/docs/unified-webhook) for detail.
              x-apidog-ignore-properties: []
            service_mode:
              type: string
              description: >
                This allows users to choose whether this specific task will get
                processed under PAYG or HYA mode. If unspecified, then this task
                will get processed under whatever mode (PAYG or HYA)
                 the user chose on the workspace setting of your account.
                - `public` means this task will be processed under PAYG mode.

                - `private` means this task will be processed under HYA mode.
              enum:
                - public
                - private
              x-apidog-enum:
                - value: public
                  name: ''
                  description: means this task will be processed under PAYG mode.
                - value: private
                  name: ''
                  description: >-
                    means this task will be processed under HYA modesetting of
                    your account.
          x-apidog-orders:
            - webhook_config
            - service_mode
          x-apidog-ignore-properties: []
      x-apidog-orders:
        - config
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```

# Image to Image

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/task:
    post:
      summary: Image to Image
      deprecated: false
      description: >-
        This is provided as part of the [Flux API](https://piapi.ai/flux-api)
        from PiAPI.  available models: 

        - Qubico/flux1-dev

        - Qubico/flux1-schnell

        - Qubico/flux1-dev-advanced 

        Check [Flux with LoRA and
        Controlnet](/docs/flux-with-lora-and-controlnet) to learn how to send
        Flux with LoRA and Controlnet task.

        Check [Flux with Redux and
        Fill](/docs/flux-redux-fill-variation-inpaint-outpaint) to learn how to
        send Flux with variation, inpaint and out paint task.



        Below is an example of  ***image-to-image*** request and response.
      operationId: flux-api/image-to-image
      tags:
        - Endpoints/Flux/Create Task
        - FLUX
      parameters:
        - name: X-API-Key
          in: header
          description: Your API KEY used for request authorization
          required: true
          example: ''
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  description: the model name
                  enum:
                    - Qubico/flux1-dev
                    - Qubico/flux1-schnell
                    - Qubico/flux1-dev-advanced
                  x-apidog-enum:
                    - value: Qubico/flux1-dev
                      name: ''
                      description: ''
                    - value: Qubico/flux1-schnell
                      name: ''
                      description: ''
                    - value: Qubico/flux1-dev-advanced
                      name: ''
                      description: ''
                task_type:
                  type: string
                  enum:
                    - img2img
                    - img2img-lora
                    - controlnet-lora
                  x-apidog-enum:
                    - value: img2img
                      name: ''
                      description: ''
                    - value: img2img-lora
                      name: ''
                      description: ''
                    - value: controlnet-lora
                      name: ''
                      description: ''
                input:
                  type: object
                  properties:
                    prompt:
                      type: string
                    negative_prompt:
                      type: string
                    denoise:
                      type: number
                      default: 0.7
                      minimum: 0
                      maximum: 1
                      exclusiveMinimum: true
                    guidance_scale:
                      type: number
                      description: >-
                        Guidance scale for image generation. High guidance
                        scales improve prompt adherence at the cost of reduced
                        realism.
                      minimum: 1.5
                      maximum: 5
                    image:
                      type: string
                    batch_size:
                      type: number
                      default: 1
                      minimum: 1
                      maximum: 4
                      description: >-
                        number of images, only works for schnell at the moment.
                        Price will be 

                        batch_size * (price for one generation)
                    lora_settings:
                      type: array
                      items:
                        type: object
                        x-apidog-refs:
                          01JE6EQR077DHE7FVP7EH0ZC6S:
                            $ref: '#/components/schemas/lora_setting'
                            x-apidog-overrides:
                              lora_type: &ref_0
                                type: string
                                description: >-
                                  name of the lora model, check [Available LoRA
                                  and
                                  Controlnet](/docs/available-lora-and-controlnet)
                            required:
                              - lora_type
                        x-apidog-orders:
                          - 01JE6EQR077DHE7FVP7EH0ZC6S
                        properties:
                          lora_type: *ref_0
                          lora_image:
                            type: string
                            description: optional
                          lora_strength:
                            type: number
                            description: optional
                        required:
                          - lora_type
                        x-apidog-ignore-properties:
                          - lora_type
                          - lora_image
                          - lora_strength
                    control_net_settings:
                      type: array
                      items:
                        $ref: '#/components/schemas/control_net_setting'
                  required:
                    - prompt
                    - image
                    - control_net_settings
                  x-apidog-orders:
                    - prompt
                    - negative_prompt
                    - denoise
                    - guidance_scale
                    - image
                    - batch_size
                    - lora_settings
                    - control_net_settings
                  description: the input param of the flux task
                  x-apidog-refs: {}
                  x-apidog-ignore-properties: []
                config:
                  type: object
                  properties:
                    webhook_config:
                      type: object
                      properties:
                        endpoint:
                          type: string
                        secret:
                          type: string
                      x-apidog-orders:
                        - endpoint
                        - secret
                      x-apidog-ignore-properties: []
                  x-apidog-orders:
                    - webhook_config
                  x-apidog-ignore-properties: []
              required:
                - model
                - task_type
                - input
              x-apidog-orders:
                - model
                - task_type
                - input
                - config
              x-apidog-ignore-properties: []
            example:
              model: Qubico/flux1-schnell
              task_type: img2img
              input:
                prompt: a bear
                image: https://i.ibb.co/J7ZNgSG/01.jpg
              config:
                webhook_config:
                  endpoint: https://webhook.site/xxxx
                  secret: ''
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      task_id:
                        type: string
                      model:
                        type: string
                      task_type:
                        type: string
                      status:
                        type: string
                        enum:
                          - Completed
                          - Processing
                          - Pending
                          - Failed
                          - Staged
                        x-apidog-enum:
                          - value: Completed
                            name: ''
                            description: ''
                          - value: Processing
                            name: ''
                            description: >-
                              Means that your jobs is currently being processed.
                              Number of "processing" jobs counts as part of the
                              "concurrent jobs"
                          - value: Pending
                            name: ''
                            description: >-
                              Means that we recognizes the jobs you sent should
                              be processed by MJ/Luma/Suno/Kling/etc but right
                              now none of the  account is available to receive
                              further jobs. During peak loads there can be
                              longer wait time to get your jobs from "pending"
                              to "processing". If reducing waiting time is your
                              primary concern, then a combination of
                              Pay-as-you-go and Host-your-own-account option
                              might suit you better.Number of "pending" jobs
                              counts as part of the "concurrent jobs"
                          - value: Failed
                            name: ''
                            description: Task failed. Check the error message for detail.
                          - value: Staged
                            name: ''
                            description: >-
                              A stage only in Midjourney task . Means that you
                              have exceeded the number of your "concurrent jobs"
                              limit and your jobs are being queuedNumber of
                              "staged" jobs does not count as part of the
                              "concurrent jobs". Also, please note the maximum
                              number of jobs in the "staged" queue is 50. So if
                              your operational needs exceed the 50 jobs limit,
                              then please create your own queuing system logic. 
                        description: >-
                          Hover on the "Completed" option and you coult see the
                          explaintion of all status:
                          completed/processing/pending/failed/staged
                      input:
                        type: object
                        properties: {}
                        x-apidog-orders: []
                        x-apidog-ignore-properties: []
                      output:
                        type: object
                        properties:
                          image_url:
                            type: string
                            description: when result contains 1 image
                          image_urls:
                            type: array
                            items:
                              type: string
                            description: when result contains multiple images
                        x-apidog-orders:
                          - image_url
                          - image_urls
                        x-apidog-ignore-properties: []
                      meta:
                        type: object
                        properties:
                          created_at:
                            type: string
                            description: >-
                              The time when the task was submitted to us (staged
                              and/or pending)
                          started_at:
                            type: string
                            description: >-
                              The time when the task started processing. the
                              time from created_at to time of started_at is time
                              the job spent in the "staged“ stage and/or
                              the"pending" stage if there were any.
                          ended_at:
                            type: string
                            description: The time when the task finished processing.
                          usage:
                            type: object
                            properties:
                              type:
                                type: string
                              frozen:
                                type: number
                              consume:
                                type: number
                            x-apidog-orders:
                              - type
                              - frozen
                              - consume
                            required:
                              - type
                              - frozen
                              - consume
                            x-apidog-ignore-properties: []
                          is_using_private_pool:
                            type: boolean
                        x-apidog-orders:
                          - created_at
                          - started_at
                          - ended_at
                          - usage
                          - is_using_private_pool
                        required:
                          - usage
                          - is_using_private_pool
                        x-apidog-ignore-properties: []
                      detail:
                        type: 'null'
                      logs:
                        type: array
                        items:
                          type: object
                          properties: {}
                          x-apidog-orders: []
                          x-apidog-ignore-properties: []
                      error:
                        type: object
                        properties:
                          code:
                            type: integer
                          message:
                            type: string
                        x-apidog-orders:
                          - code
                          - message
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    required:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    x-apidog-ignore-properties: []
                  message:
                    type: string
                    description: >-
                      If you get non-null error message, here are some steps you
                      chould follow:

                      - Check our [common error
                      message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)

                      - Retry for several times

                      - If you have retried for more than 3 times and still not
                      work, file a ticket on Discord and our support will be
                      with you soon.
                x-apidog-orders:
                  - code
                  - data
                  - message
                x-apidog-refs: {}
                required:
                  - code
                  - data
                  - message
                x-apidog-ignore-properties: []
              example:
                code: 200
                data:
                  task_id: 1631d053-2352-4add-95cc-360fc52d5f89
                  model: Qubico/flux1-schnell
                  task_type: img2img
                  status: pending
                  config:
                    webhook_config:
                      endpoint: https://webhook.site/xxxx
                      secret: ''
                  input:
                    prompt: a bear
                    negative_prompt: ''
                    image: https://i.ibb.co/J7ZNgSG/01.jpg
                    width: 0
                    height: 0
                    steps: 0
                  output: null
                  meta:
                    created_at: '2024-09-25T07:40:08.333962391Z'
                    started_at: '0001-01-01T00:00:00Z'
                    ended_at: '0001-01-01T00:00:00Z'
                    usage:
                      type: quota
                      frozen: 0
                      consume: 20000
                    is_using_private_pool: false
                  detail: null
                  logs: []
                  error:
                    code: 0
                    raw_message: ''
                    message: ''
                    detail: null
                message: success
          headers: {}
          x-apidog-name: Success
      security: []
      x-apidog-folder: Endpoints/Flux/Create Task
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-10308981-run
components:
  schemas:
    control_net_setting:
      type: object
      properties:
        control_type:
          type: string
        control_image:
          type: string
      x-apidog-orders:
        - control_type
        - control_image
      required:
        - control_type
        - control_image
      description: >-
        Check [Flux with LoRA and
        Controlnet](/docs/flux-with-lora-and-controlnet) 
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
    lora_setting:
      type: object
      properties:
        lora_type:
          type: string
          description: >-
            name of the lora model, check [Available LoRA and
            Controlnet](/docs/available-lora-and-controlnet)
        lora_image:
          type: string
          description: optional
        lora_strength:
          type: number
          description: optional
      x-apidog-orders:
        - lora_type
        - lora_image
        - lora_strength
      description: >-
        Check [Flux with LoRA and
        Controlnet](/docs/flux-with-lora-and-controlnet) 
      required:
        - lora_type
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```

# Kontext

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/task:
    post:
      summary: Kontext
      deprecated: false
      description: >-
        This is provided as part of the [Flux API](https://piapi.ai/flux-api)
        from PiAPI.

        Available models: 

        - Qubico/flux1-dev-advanced 


        Available task type:

        - kontext
      operationId: flux-api/kontext
      tags:
        - Endpoints/Flux/Create Task
        - FLUX
      parameters:
        - name: X-API-Key
          in: header
          description: Your API KEY used for request authorization
          required: true
          example: ''
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  description: the model name
                  enum:
                    - Qubico/flux1-dev-advanced
                  x-apidog-enum:
                    - value: Qubico/flux1-dev-advanced
                      name: ''
                      description: ''
                task_type:
                  type: string
                  enum:
                    - kontext
                  x-apidog-enum:
                    - value: kontext
                      name: ''
                      description: ''
                input:
                  type: object
                  properties:
                    prompt:
                      type: string
                      description: text desciption of how the input image to be edited
                    image:
                      type: string
                      description: input image, url or base64 string
                    width:
                      type: integer
                      description: width of the output image
                    height:
                      type: integer
                      default: 1024
                      description: height of the output image
                    seed:
                      type: integer
                      description: random seed for generation if not provided
                      default: -1
                    steps:
                      type: integer
                      default: 28
                      maximum: 40
                      description: steps used to generate
                  required:
                    - prompt
                    - image
                  x-apidog-orders:
                    - prompt
                    - image
                    - width
                    - height
                    - seed
                    - steps
                  description: the input param of the flux task
                  x-apidog-refs: {}
                config:
                  type: object
                  properties:
                    webhook_config:
                      type: object
                      properties:
                        endpoint:
                          type: string
                        secret:
                          type: string
                      x-apidog-orders:
                        - endpoint
                        - secret
                  x-apidog-orders:
                    - webhook_config
              required:
                - model
                - task_type
                - input
              x-apidog-orders:
                - model
                - task_type
                - input
                - config
            example:
              model: Qubico/flux1-dev-advanced
              task_type: kontext
              input:
                prompt: change the word Piapi to Pineapple
                image: https://piapi.ai/dashboard/flux/input_example.png
                width: 1024
                height: 1024
                steps: 10
                seed: -1
              config:
                webhook_config:
                  endpoint: https://webhook.site/ffa17066-be55-4a1a-abf9-789286b8da44
                  secret: ''
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      task_id:
                        type: string
                      model:
                        type: string
                      task_type:
                        type: string
                      status:
                        type: string
                        enum:
                          - Completed
                          - Processing
                          - Pending
                          - Failed
                          - Staged
                        x-apidog-enum:
                          - value: Completed
                            name: ''
                            description: ''
                          - value: Processing
                            name: ''
                            description: >-
                              Means that your jobs is currently being processed.
                              Number of "processing" jobs counts as part of the
                              "concurrent jobs"
                          - value: Pending
                            name: ''
                            description: >-
                              Means that we recognizes the jobs you sent should
                              be processed by MJ/Luma/Suno/Kling/etc but right
                              now none of the  account is available to receive
                              further jobs. During peak loads there can be
                              longer wait time to get your jobs from "pending"
                              to "processing". If reducing waiting time is your
                              primary concern, then a combination of
                              Pay-as-you-go and Host-your-own-account option
                              might suit you better.Number of "pending" jobs
                              counts as part of the "concurrent jobs"
                          - value: Failed
                            name: ''
                            description: Task failed. Check the error message for detail.
                          - value: Staged
                            name: ''
                            description: >-
                              A stage only in Midjourney task . Means that you
                              have exceeded the number of your "concurrent jobs"
                              limit and your jobs are being queuedNumber of
                              "staged" jobs does not count as part of the
                              "concurrent jobs". Also, please note the maximum
                              number of jobs in the "staged" queue is 50. So if
                              your operational needs exceed the 50 jobs limit,
                              then please create your own queuing system logic. 
                        description: >-
                          Hover on the "Completed" option and you coult see the
                          explaintion of all status:
                          completed/processing/pending/failed/staged
                      input:
                        type: object
                        properties: {}
                        x-apidog-orders: []
                      output:
                        type: object
                        properties:
                          image_url:
                            type: string
                            description: when result contains 1 image
                          image_urls:
                            type: array
                            items:
                              type: string
                            description: when result contains multiple images
                        x-apidog-orders:
                          - image_url
                          - image_urls
                      meta:
                        type: object
                        properties:
                          created_at:
                            type: string
                            description: >-
                              The time when the task was submitted to us (staged
                              and/or pending)
                          started_at:
                            type: string
                            description: >-
                              The time when the task started processing. the
                              time from created_at to time of started_at is time
                              the job spent in the "staged“ stage and/or
                              the"pending" stage if there were any.
                          ended_at:
                            type: string
                            description: The time when the task finished processing.
                          usage:
                            type: object
                            properties:
                              type:
                                type: string
                              frozen:
                                type: number
                              consume:
                                type: number
                            x-apidog-orders:
                              - type
                              - frozen
                              - consume
                            required:
                              - type
                              - frozen
                              - consume
                          is_using_private_pool:
                            type: boolean
                        x-apidog-orders:
                          - created_at
                          - started_at
                          - ended_at
                          - usage
                          - is_using_private_pool
                        required:
                          - usage
                          - is_using_private_pool
                      detail:
                        type: 'null'
                      logs:
                        type: array
                        items:
                          type: object
                          properties: {}
                          x-apidog-orders: []
                      error:
                        type: object
                        properties:
                          code:
                            type: integer
                          message:
                            type: string
                        x-apidog-orders:
                          - code
                          - message
                    x-apidog-orders:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                    required:
                      - task_id
                      - model
                      - task_type
                      - status
                      - input
                      - output
                      - meta
                      - detail
                      - logs
                      - error
                  message:
                    type: string
                    description: >-
                      If you get non-null error message, here are some steps you
                      chould follow:

                      - Check our [common error
                      message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)

                      - Retry for several times

                      - If you have retried for more than 3 times and still not
                      work, file a ticket on Discord and our support will be
                      with you soon.
                x-apidog-orders:
                  - code
                  - data
                  - message
                x-apidog-refs: {}
                required:
                  - code
                  - data
                  - message
              example:
                code: 200
                data:
                  task_id: 8718d5c1-aae9-4cd5-a243-84eeb1e01117
                  model: Qubico/flux1-dev-advanced
                  task_type: kontext
                  status: completed
                  config:
                    service_mode: ''
                    webhook_config:
                      endpoint: >-
                        https://webhook.site/ffa17066-be55-4a1a-abf9-789286b8da44
                      secret: ''
                  input:
                    height: 1024
                    image: https://piapi.ai/dashboard/flux/input_example.png
                    prompt: change the word Piapi to Pineapple
                    seed: -1
                    steps: 10
                    width: 1024
                  output:
                    image_base64: ''
                    image_url: >-
                      https://img.theapi.app/temp/10f0a646-6155-4938-bf50-76934c953e9c.png
                  meta:
                    created_at: '2025-06-30T07:11:30.719851187Z'
                    started_at: '2025-06-30T07:11:31.891665902Z'
                    ended_at: '2025-06-30T07:12:03.388312371Z'
                    usage:
                      type: llm
                      frozen: 0
                      consume: 200000
                    is_using_private_pool: false
                  detail: null
                  logs: []
                  error:
                    code: 0
                    raw_message: ''
                    message: ''
                    detail: null
                message: success
          headers: {}
          x-apidog-name: Success
      security: []
      x-apidog-folder: Endpoints/Flux/Create Task
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-18588185-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```

# Get task 

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/task/{task_id}:
    get:
      summary: 'Get task '
      deprecated: false
      description: >-
        This endpoint from [PiAPI's Flux API](https://piapi.ai/flux-api)
        retrieves the output of a Flux task.
      tags:
        - Endpoints/Flux
      parameters:
        - name: task_id
          in: path
          description: ''
          required: true
          schema:
            type: string
        - name: x-api-key
          in: header
          description: Your GoAPI Key used for request authorization
          required: true
          example: ''
          schema:
            type: string
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      task_id:
                        description: important for retriving task result using Fetch API
                        type: string
                      task_type:
                        type: string
                      status:
                        type: string
                        enum:
                          - pending
                          - starting
                          - "processing\t"
                          - success
                          - failed
                          - retry
                        x-apidog-enum:
                          - value: pending
                            name: ''
                            description: the task is in wait queue of GoAPI
                          - value: starting
                            name: ''
                            description: the task is beginning to procceed
                          - value: "processing\t"
                            name: ''
                            description: rendering the task
                          - value: success
                            name: ''
                            description: task finished
                          - value: failed
                            name: ''
                            description: task failed
                          - value: retry
                            name: ''
                            description: >-
                              this usually happens if your image url is hard to
                              download
                      task_info:
                        type: object
                        properties:
                          created_at:
                            type: string
                          started_at:
                            type: string
                          completed_at:
                            type: string
                          frozen_credits:
                            type: integer
                          task_input:
                            type: object
                            properties:
                              scale:
                                type: integer
                              image:
                                type: string
                            required:
                              - scale
                              - image
                            x-apidog-orders:
                              - scale
                              - image
                        required:
                          - created_at
                          - started_at
                          - completed_at
                          - frozen_credits
                          - task_input
                        x-apidog-orders:
                          - created_at
                          - started_at
                          - completed_at
                          - frozen_credits
                          - task_input
                      task_result:
                        type: object
                        properties:
                          used_credits:
                            type: integer
                          error_messages:
                            type: array
                            items:
                              type: string
                          task_output:
                            type: object
                            properties:
                              image_base64:
                                type: string
                              image_url:
                                type: string
                            required:
                              - image_base64
                              - image_url
                            x-apidog-orders:
                              - image_base64
                              - image_url
                        required:
                          - used_credits
                          - error_messages
                          - task_output
                        x-apidog-orders:
                          - used_credits
                          - error_messages
                          - task_output
                    required:
                      - task_id
                      - task_type
                      - status
                      - task_info
                      - task_result
                    x-apidog-orders:
                      - task_id
                      - task_type
                      - status
                      - task_info
                      - task_result
                  message:
                    type: string
                required:
                  - code
                  - data
                  - message
                x-apidog-orders:
                  - code
                  - data
                  - message
              example:
                code: 200
                data:
                  task_id: a62ba0d0-184f-xxxx79f
                  model: Qubico/flux1-dev
                  task_type: txt2img
                  status: success
                  config:
                    service_mode: ''
                    webhook_config:
                      endpoint: ''
                      secret: ''
                  input:
                    prompt: a bear
                  output:
                    image_url: https://ixxxxe3f.png
                    image_base64: ''
                  meta:
                    created_at: '2024-10-23T10:35:31.039487176Z'
                    started_at: '0001-01-01T00:00:00Z'
                    ended_at: '0001-01-01T00:00:00Z'
                  detail: null
                  logs: []
                  error:
                    code: 0
                    raw_message: ''
                    message: ''
                    detail: null
                message: success
          headers: {}
          x-apidog-name: Success
      security: []
      x-apidog-folder: Endpoints/Flux
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/675356/apis/api-10259089-run
components:
  schemas: {}
  securitySchemes: {}
servers:
  - url: https://api.piapi.ai
    description: Develop Env
security: []

```





