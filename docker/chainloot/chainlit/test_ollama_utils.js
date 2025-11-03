const ollamaUtils = require('@huggingface/ollama-utils');

console.log('Available exports:');
console.log(Object.keys(ollamaUtils));

// Test the API
console.log('\nTesting with SmolLM3 template...');

// SmolLM3 template from the model card
const smollm3Template = `{%- for message in messages %}
    {%- if message['role'] == 'user' %}
        {%- if loop.first %}
<|im_start|>user
{{ message['content'] }}<|im_end|>
        {%- else %}
<|im_start|>user
{{ message['content'] }}<|im_end|>
        {%- endif %}
    {%- elif message['role'] == 'assistant' %}
        {%- if 'thoughts' in message %}
<|im_start|>assistant
<think>
{{ message['thoughts'] }}
</think>

{{ message['content'] }}<|im_end|>
        {%- else %}
<|im_start|>assistant
{{ message['content'] }}<|im_end|>
        {%- endif %}
    {%- elif message['role'] == 'system' %}
<|im_start|>system
{{ message['content'] }}<|im_end|>
    {%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
<|im_start|>assistant
{%- endif %}`;

const ggufInfo = {
    chat_template: smollm3Template,
    bos_token: '<|im_start|>',
    eos_token: '<|im_end|>'
};

try {
    if (ollamaUtils.convertGGUFTemplateToOllama) {
        const result = ollamaUtils.convertGGUFTemplateToOllama(ggufInfo);
        console.log('Conversion result:');
        console.log(JSON.stringify(result, null, 2));
    } else {
        console.log('convertGGUFTemplateToOllama not found');
    }
} catch (error) {
    console.error('Error during conversion:', error);
}
