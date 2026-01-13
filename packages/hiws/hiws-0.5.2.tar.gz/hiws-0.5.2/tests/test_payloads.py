import pytest
from hiws.types import Update
from hiws.types.message import (
    TextMessage,
    ImageMessage,
    AudioMessage,
    DocumentMessage,
    LocationMessage,
    QuickReplyButtonMessage,
    ContactMessage,
    InteractiveMessage,
    UnsupportedMessage,
)


def test_text_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Sheena Nelson"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgLMTY1M...",
                                    "timestamp": "1654806835",
                                    "text": {"body": "Hello world"},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert update.object == "whatsapp_business_account"
    assert update.message is not None
    assert isinstance(update.message, TextMessage)
    assert update.message.text.body == "Hello world"
    assert update.message.from_phone_number == "16505551234"
    assert update.contact is not None and update.contact.profile.name == "Sheena Nelson"


def test_image_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "106540352242922",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15558042491",
                                "phone_number_id": "1077549164481542",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Peter Parker"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgMNTg0MjQ2MjI5MTEyFQIAEhgWM0VCMDZCNjA4MEFFNUM5MjgyNUVFRgA=",
                                    "timestamp": "1767134702",
                                    "type": "image",
                                    "image": {
                                        "mime_type": "image/jpeg",
                                        "sha256": "ROJh6NYjLY1bSuLrijox7AfXp64b2U/lnNSL96mWWVE=",
                                        "id": "898613572721859",
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert isinstance(update.message, ImageMessage)
    assert update.message.image.caption is None
    assert update.message.image.mime_type == "image/jpeg"
    assert update.message.image.id == "898613572721859"


def test_audio_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Luke Skywalker"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgLMTY1M...",
                                    "timestamp": "1654806835",
                                    "type": "audio",
                                    "audio": {
                                        "mime_type": "audio/ogg; codecs=opus",
                                        "sha256": "somehash",
                                        "id": "audio-id",
                                        "voice": True,
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert isinstance(update.message, AudioMessage)
    assert update.message.audio.mime_type == "audio/ogg; codecs=opus"
    assert update.message.audio.id == "audio-id"
    assert update.message.audio.voice is True


def test_document_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Tony Stark"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgLMTY1M...",
                                    "timestamp": "1654806835",
                                    "type": "document",
                                    "document": {
                                        "caption": "My Document",
                                        "filename": "file.pdf",
                                        "mime_type": "application/pdf",
                                        "sha256": "somehash",
                                        "id": "doc-id",
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert isinstance(update.message, DocumentMessage)
    assert update.message.document.caption == "My Document"
    assert update.message.document.filename == "file.pdf"
    assert update.message.document.mime_type == "application/pdf"
    assert update.message.document.id == "doc-id"


def test_location_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Natasha Romanoff"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgLMTY1M...",
                                    "timestamp": "1654806835",
                                    "type": "location",
                                    "location": {
                                        "latitude": 37.483307,
                                        "longitude": -122.148381,
                                        "name": "Meta HQ",
                                        "address": "1 Hacker Way, Menlo Park, CA 94025",
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert isinstance(update.message, LocationMessage)
    assert update.message.location.latitude == 37.483307
    assert update.message.location.longitude == -122.148381
    assert update.message.location.name == "Meta HQ"
    assert update.message.location.address == "1 Hacker Way, Menlo Park, CA 94025"


def test_quick_reply_button_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Steve Rogers"},
                                    "wa_id": "<WHATSAPP_USER_ID>",
                                }
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                        "id": "<CONTEXTUAL_WHATSAPP_MESSAGE_ID>",
                                    },
                                    "from": "<WHATSAPP_USER_PHONE_NUMBER>",
                                    "id": "<WHATSAPP_MESSAGE_ID>",
                                    "timestamp": "<WEBHOOK_TRIGGER_TIMESTAMP>",
                                    "type": "button",
                                    "button": {
                                        "payload": "<BUTTON_LABEL_TEXT>",
                                        "text": "<BUTTON_LABEL_TEXT>",
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert isinstance(update.message, QuickReplyButtonMessage)
    assert update.message.button.text == "<BUTTON_LABEL_TEXT>"
    assert update.message.button.payload == "<BUTTON_LABEL_TEXT>"


def test_contact_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "<WHATSAPP_USER_PROFILE_NAME>"},
                                    "wa_id": "<WHATSAPP_USER_ID>",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "<WHATSAPP_USER_PHONE_NUMBER>",
                                    "id": "<WHATSAPP_MESSAGE_ID>",
                                    "timestamp": "<WEBHOOK_TRIGGER_TIMESTAMP>",
                                    "type": "contacts",
                                    "contacts": [
                                        {
                                            "addresses": [
                                                {
                                                    "city": "<CONTACT_CITY>",
                                                    "country": "<CONTACT_COUNTRY>",
                                                    "country_code": "<CONTACT_COUNTRY_CODE>",
                                                    "state": "<CONTACT_STATE>",
                                                    "street": "<CONTACT_STREET>",
                                                    "type": "HOME",
                                                    "zip": "<CONTACT_ZIP>",
                                                }
                                            ],
                                            "birthday": "<CONTACT_BIRTHDAY>",
                                            "emails": [
                                                {
                                                    "email": "<CONTACT_EMAIL>",
                                                    "type": "WORK",
                                                }
                                            ],
                                            "name": {
                                                "formatted_name": "<CONTACT_FORMATTED_NAME>",
                                                "first_name": "<CONTACT_FIRST_NAME>",
                                                "last_name": "<CONTACT_LAST_NAME>",
                                                "middle_name": "<CONTACT_MIDDLE_NAME>",
                                                "suffix": "<CONTACT_NAME_SUFFIX>",
                                                "prefix": "<CONTACT_NAME_PREFIX>",
                                            },
                                            "org": {
                                                "company": "<CONTACT_ORG_COMPANY>",
                                                "department": "<CONTACT_ORG_DEPARTMENT>",
                                                "title": "<CONTACT_ORG_TITLE>",
                                            },
                                            "phones": [
                                                {
                                                    "phone": "<CONTACT_PHONE>",
                                                    "wa_id": "<CONTACT_WHATSAPP_PHONE_NUMBER>",
                                                    "type": "MOBILE",
                                                }
                                            ],
                                            "urls": [
                                                {"url": "<CONTACT_URL>", "type": "HOME"}
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)

    assert isinstance(update.message, ContactMessage)
    assert len(update.message.contacts) == 1
    contact = update.message.contacts[0]
    assert contact.name
    assert contact.name.first_name == "<CONTACT_FIRST_NAME>"
    assert contact.phones
    assert contact.phones[0].phone == "<CONTACT_PHONE>"
    assert contact.emails
    assert contact.emails[0].email == "<CONTACT_EMAIL>"
    assert contact.addresses
    assert contact.addresses[0].city == "<CONTACT_CITY>"
    assert contact.org
    assert contact.org.company == "<CONTACT_ORG_COMPANY>"
    assert contact.urls
    assert contact.urls[0].url == "<CONTACT_URL>"


def test_interactive_list_reply_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "<WHATSAPP_USER_PROFILE_NAME>"},
                                    "wa_id": "<WHATSAPP_USER_ID>",
                                }
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                        "id": "<CONTEXTUAL_WHATSAPP_MESSAGE_ID>",
                                    },
                                    "from": "<WHATSAPP_USER_PHONE_NUMBER>",
                                    "id": "<WHATSAPP_MESSAGE_ID>",
                                    "timestamp": "<WEBHOOK_TRIGGER_TIMESTAMP>",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "list_reply",
                                        "list_reply": {
                                            "id": "<ROW_ID>",
                                            "title": "<ROW_TITLE>",
                                            "description": "<ROW_DESCRIPTION>",
                                        },
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    update = Update.model_validate(payload)
    assert isinstance(update.message, InteractiveMessage)
    assert update.message.interactive.type == "list_reply"
    assert update.message.interactive.list_reply is not None
    assert update.message.interactive.list_reply.id == "<ROW_ID>"
    assert update.message.interactive.list_reply.title == "<ROW_TITLE>"
    assert update.message.interactive.list_reply.description == "<ROW_DESCRIPTION>"


def test_interactive_button_reply_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "<WHATSAPP_USER_PROFILE_NAME>"},
                                    "wa_id": "<WHATSAPP_USER_ID>",
                                }
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                        "id": "<CONTEXTUAL_WHATSAPP_MESSAGE_ID>",
                                    },
                                    "from": "<WHATSAPP_USER_PHONE_NUMBER>",
                                    "id": "<WHATSAPP_MESSAGE_ID>",
                                    "timestamp": "<WEBHOOK_TRIGGER_TIMESTAMP>",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "<BUTTON_ID>",
                                            "title": "<BUTTON_LABEL_TEXT>",
                                        },
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    update = Update.model_validate(payload)
    assert isinstance(update.message, InteractiveMessage)
    assert update.message.interactive.type == "button_reply"
    assert update.message.interactive.button_reply is not None
    assert update.message.interactive.button_reply.id == "<BUTTON_ID>"
    assert update.message.interactive.button_reply.title == "<BUTTON_LABEL_TEXT>"


def test_status_update_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.HBgLMTY1M...",
                                    "status": "delivered",
                                    "timestamp": "1654806835",
                                    "recipient_id": "16505551234",
                                    "conversation": {
                                        "id": "some-conversation-id",
                                        "origin": {"type": "user_initiated"},
                                    },
                                    "pricing": {
                                        "billable": True,
                                        "pricing_model": "CBP",
                                        "category": "business_initiated",
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    update = Update.model_validate(payload)
    assert update.message is None
    assert update.status is not None
    assert update.status.status == "delivered"
    assert update.status.recipient_id == "16505551234"


def test_unsupported_message_payload():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "102290129340398",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550783881",
                                "phone_number_id": "106540352242922",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Sheena Nelson"},
                                    "wa_id": "16505551234",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "16505551234",
                                    "id": "wamid.HBgLMTY1MDM4Nzk0MzkVAgASGBQzQUFERjg0NDEzNDdFODU3MUMxMAA=",
                                    "timestamp": "1750090702",
                                    "errors": [
                                        {
                                            "code": 131051,
                                            "title": "Message type unknown",
                                            "message": "Message type unknown",
                                            "error_data": {
                                                "details": "Message type is currently not supported."
                                            },
                                        }
                                    ],
                                    "type": "unsupported",
                                    "unsupported": {"type": "edit"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    update = Update.model_validate(payload)
    assert isinstance(update.message, UnsupportedMessage)
    assert len(update.message.errors) == 1
    error = update.message.errors[0]
    assert error.code == 131051
    assert error.title == "Message type unknown"
    assert error.message == "Message type unknown"
    assert error.error_data.details == "Message type is currently not supported."
    assert update.message.unsupported.type == "edit"
