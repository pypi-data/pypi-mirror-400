---
title: webhook
description: Webhook Module.
---

# webhook module

Webhook Module.

<a id="wriftai.webhook.NoSignatureError"></a>

### *exception* NoSignatureError

Bases: [`SignatureVerificationError`](#wriftai.webhook.SignatureVerificationError)

Initialize NoSignatureError.

* **Return type:**
  None

<a id="wriftai.webhook.NoTimestampError"></a>

### *exception* NoTimestampError

Bases: [`SignatureVerificationError`](#wriftai.webhook.SignatureVerificationError)

Initialize NoTimestampError.

* **Return type:**
  None

<a id="wriftai.webhook.SignatureMismatchError"></a>

### *exception* SignatureMismatchError

Bases: [`SignatureVerificationError`](#wriftai.webhook.SignatureVerificationError)

Initialize SignatureMismatchError.

* **Return type:**
  None

<a id="wriftai.webhook.SignatureVerificationError"></a>

### *exception* SignatureVerificationError

Bases: `ValueError`

Exceptions raised when webhook signature verification fails.

<a id="wriftai.webhook.TimestampOutsideToleranceError"></a>

### *exception* TimestampOutsideToleranceError

Bases: [`SignatureVerificationError`](#wriftai.webhook.SignatureVerificationError)

Initialize TimestampOutsideToleranceError.

* **Return type:**
  None