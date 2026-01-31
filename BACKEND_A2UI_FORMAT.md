# Backend A2UI Response Format

This document describes the JSON response format expected by the frontend to support A2UI (Agent-to-UI) protocol v0.8.

## Overview

The frontend now supports **both plain text and A2UI protocol messages**. When the backend returns A2UI data, the frontend will render interactive UI components (forms, buttons, inputs, etc.) directly within the chat interface.

## Response Format

### Current Format (Plain Text) - Still Supported

```json
{
  "success": true,
  "reply": "I can help you with GST filing. Please provide your GSTIN number."
}
```

### New Format (With A2UI Protocol)

```json
{
  "success": true,
  "reply": "I can help you with GST filing. Please fill in the form below:",
  "a2ui_message": {
    "version": "0.8",
    "surfaces": [
      {
        "id": "gst_form",
        "components": [
          {
            "id": "heading",
            "type": "Heading",
            "level": 3,
            "text": "GST Filing Information"
          },
          {
            "id": "input_gstin",
            "type": "TextInput",
            "label": "GSTIN Number",
            "placeholder": "Enter your 15-digit GSTIN",
            "value": "form.gstin",
            "required": true
          },
          {
            "id": "input_period",
            "type": "Select",
            "label": "Filing Period",
            "value": "form.period",
            "options": [
              { "value": "Q1_2024", "label": "Q1 2024" },
              { "value": "Q2_2024", "label": "Q2 2024" },
              { "value": "Q3_2024", "label": "Q3 2024" },
              { "value": "Q4_2024", "label": "Q4 2024" }
            ],
            "required": true
          },
          {
            "id": "submit_btn",
            "type": "Button",
            "label": "Submit",
            "variant": "primary",
            "action": {
              "type": "submit_gst_form",
              "data": {
                "gstin": "{{ form.gstin }}",
                "period": "{{ form.period }}"
              }
            }
          }
        ]
      }
    ]
  }
}
```

## A2UI Protocol v0.8 Components

### Layout Components

#### Container
```json
{
  "id": "container_id",
  "type": "Container",
  "children": ["child_component_id_1", "child_component_id_2"]
}
```

#### Stack
```json
{
  "id": "stack_id",
  "type": "Stack",
  "direction": "vertical",  // or "horizontal"
  "spacing": 2,
  "children": ["component_1", "component_2"]
}
```

### Text Components

#### Text
```json
{
  "id": "text_id",
  "type": "Text",
  "text": "This is some text content"
}
```

#### Heading
```json
{
  "id": "heading_id",
  "type": "Heading",
  "level": 2,  // 1-6
  "text": "Section Title"
}
```

### Input Components

#### TextInput
```json
{
  "id": "text_input_id",
  "type": "TextInput",
  "label": "Field Label",
  "placeholder": "Enter text...",
  "value": "form.fieldName",  // Data binding path
  "required": true,
  "disabled": false
}
```

#### NumberInput
```json
{
  "id": "number_input_id",
  "type": "NumberInput",
  "label": "Amount",
  "placeholder": "0.00",
  "value": "form.amount",
  "min": 0,
  "max": 1000000,
  "required": true
}
```

#### DateInput
```json
{
  "id": "date_input_id",
  "type": "DateInput",
  "label": "Due Date",
  "value": "form.dueDate",
  "required": true
}
```

#### Select (Dropdown)
```json
{
  "id": "select_id",
  "type": "Select",
  "label": "Choose Option",
  "value": "form.selection",
  "options": [
    { "value": "option1", "label": "Option 1" },
    { "value": "option2", "label": "Option 2" },
    { "value": "option3", "label": "Option 3" }
  ],
  "required": true
}
```

#### Checkbox
```json
{
  "id": "checkbox_id",
  "type": "Checkbox",
  "label": "I agree to terms",
  "value": "form.agreedToTerms"
}
```

#### Radio
```json
{
  "id": "radio_id",
  "type": "Radio",
  "label": "Select One",
  "value": "form.choice",
  "options": [
    { "value": "yes", "label": "Yes" },
    { "value": "no", "label": "No" }
  ],
  "required": true
}
```

### Action Components

#### Button
```json
{
  "id": "button_id",
  "type": "Button",
  "label": "Submit Form",
  "variant": "primary",  // or "secondary", "outline", "ghost"
  "disabled": false,
  "action": {
    "type": "custom_action_name",
    "data": {
      "field1": "{{ form.field1 }}",
      "field2": "{{ form.field2 }}"
    }
  }
}
```

### Form Component

#### Form (Groups inputs together)
```json
{
  "id": "form_id",
  "type": "Form",
  "children": ["input1", "input2", "submit_button"]
}
```

## Data Binding

Use the `value` property with dot notation to bind inputs to form state:

```json
{
  "type": "TextInput",
  "value": "form.userData.email"
}
```

In actions, reference the bound values using template syntax:

```json
{
  "action": {
    "type": "submit",
    "data": {
      "email": "{{ form.userData.email }}"
    }
  }
}
```

## Action Handling

When a user interacts with A2UI components (e.g., clicks a button), the frontend sends the action back to the backend:

### Request from Frontend
```json
{
  "conversation_id": "7aaefde3-5c16-400a-a518-9ff8649d384f",
  "message": "{\"type\":\"submit_gst_form\",\"data\":{\"gstin\":\"29ABCDE1234F1Z5\",\"period\":\"Q1_2024\"}}"
}
```

The `message` field contains a **stringified JSON** of the action object.

### Backend Should Parse and Respond

1. Parse the `message` field as JSON
2. Check the `type` field to determine the action
3. Extract data from the `data` field
4. Process the action (e.g., validate GSTIN, start GST filing process)
5. Return a new A2UI message or plain text response

## Complete Example: Multi-Step Form

### Step 1: Backend asks for basic info

```json
{
  "success": true,
  "reply": "Let's start your ITR filing. Please provide your basic information:",
  "a2ui_message": {
    "version": "0.8",
    "surfaces": [
      {
        "id": "itr_step1",
        "components": [
          {
            "id": "pan_input",
            "type": "TextInput",
            "label": "PAN Number",
            "placeholder": "ABCDE1234F",
            "value": "form.pan",
            "required": true
          },
          {
            "id": "financial_year",
            "type": "Select",
            "label": "Financial Year",
            "value": "form.fy",
            "options": [
              { "value": "2023-24", "label": "2023-24" },
              { "value": "2022-23", "label": "2022-23" }
            ],
            "required": true
          },
          {
            "id": "next_btn",
            "type": "Button",
            "label": "Next",
            "variant": "primary",
            "action": {
              "type": "itr_basic_info_submit",
              "data": {
                "pan": "{{ form.pan }}",
                "fy": "{{ form.fy }}"
              }
            }
          }
        ]
      }
    ]
  }
}
```

### Step 2: User submits, backend receives action

Frontend sends:
```json
{
  "conversation_id": "xxx",
  "message": "{\"type\":\"itr_basic_info_submit\",\"data\":{\"pan\":\"ABCDE1234F\",\"fy\":\"2023-24\"}}"
}
```

### Step 3: Backend validates and asks for income details

```json
{
  "success": true,
  "reply": "Great! Now let's gather your income information:",
  "a2ui_message": {
    "version": "0.8",
    "surfaces": [
      {
        "id": "itr_step2",
        "components": [
          {
            "id": "salary_income",
            "type": "NumberInput",
            "label": "Salary Income (₹)",
            "value": "form.salary",
            "min": 0,
            "required": true
          },
          {
            "id": "other_income",
            "type": "NumberInput",
            "label": "Other Income (₹)",
            "value": "form.otherIncome",
            "min": 0
          },
          {
            "id": "submit_btn",
            "type": "Button",
            "label": "Submit ITR",
            "variant": "primary",
            "action": {
              "type": "submit_itr",
              "data": {
                "pan": "ABCDE1234F",
                "fy": "2023-24",
                "salary": "{{ form.salary }}",
                "otherIncome": "{{ form.otherIncome }}"
              }
            }
          }
        ]
      }
    ]
  }
}
```

## Backend Implementation Checklist

- [ ] Check if incoming `message` is stringified JSON (starts with `{`)
- [ ] Parse action JSON and extract `type` and `data`
- [ ] Route actions to appropriate handlers based on `type`
- [ ] Validate user inputs from `data` field
- [ ] Generate appropriate A2UI response or plain text
- [ ] Include both `reply` (text) and `a2ui_message` (UI) in response
- [ ] Handle errors gracefully with plain text fallback

## Benefits of A2UI

1. **Dynamic UI**: AI can request exactly the data it needs without hardcoded forms
2. **Type Safety**: Structured data collection vs. parsing free text
3. **Better UX**: Progressive disclosure - show forms only when needed
4. **Validation**: Client-side validation rules from backend
5. **Flexibility**: Change UI requirements without frontend deployments

## Testing Without A2UI

The frontend fully supports plain text responses. If you don't include `a2ui_message`, the frontend will render the `reply` as before. This means:

- **Backward compatible**: Existing plain text responses continue to work
- **Gradual migration**: Add A2UI for specific flows one at a time
- **Fallback safe**: If A2UI rendering fails, plain text is always shown

## Additional Resources

- [A2UI SDK Documentation](https://a2ui-sdk.js.org/)
- [A2UI Specification](https://a2ui.org/)
- Frontend A2UI component: `src/components/common/A2UIChatMessage.tsx`
- Frontend types: `src/types/index.ts`
