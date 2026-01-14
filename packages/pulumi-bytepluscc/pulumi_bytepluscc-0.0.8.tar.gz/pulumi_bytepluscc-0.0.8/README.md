
# Bytepluscc Resource Provider

The Bytepluscc resource provider for Pulumi lets you use byteplus resources in your cloud programs.  To use
this package, please [install the Pulumi CLI first](https://pulumi.io/).

## Installing

This package is available in many languages in the standard packaging formats.

### Node.js (Java/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

    $ npm install @byteplus/pulumi-bytepluscc

or `yarn`:

    $ yarn add @byteplus/pulumi-bytepluscc

### Python

To use from Python, install using `pip`:

    $ pip install pulumi_bytepluscc

### Go

To use from Go, use `go get` to grab the latest version of the library

    $ go get github.com/byteplus-sdk/pulumi-bytepluscc/sdk

### .NET

To use from .NET, install using `dotnet add package`:

    $ dotnet add package Byteplus.Pulumi.Bytepluscc


## Configuration Reference

In addition to generic `provider` arguments
(e.g. `alias` and `version`), the following arguments are supported in the Bytepluscc
provider configuration:

### Optional

- `accessKey` (String) The Access Key for Byteplus Provider. It must be provided, but it can also be sourced from the `BYTEPLUS_ACCESS_KEY` environment variable
- `secretKey` (String) he Secret Key for Byteplus Provider. It must be provided, but it can also be sourced from the `BYTEPLUS_SECRET_KEY` environment variable
- `assumeRole` (Attributes) An `assume_role` block (documented below). Only one `assume_role` block may be in the configuration. (see [below for nested schema](#nestedatt--assume_role))
- `customerHeaders` (String) CUSTOMER HEADERS for Byteplus Provider. The customer_headers field uses commas (,) to separate multiple headers, and colons (:) to separate each header key from its corresponding value.
- `disableSsl` (Boolean) Disable SSL for Byteplus Provider
- `endpoints` (Attributes) An `endpoints` block (documented below). Only one `endpoints` block may be in the configuration. (see [below for nested schema](#nestedatt--endpoints))
- `proxyUrl` (String) PROXY URL for Byteplus Provider
- `region` (String) The Region for Byteplus Provider. It must be provided, but it can also be sourced from the `BYTEPLUS_REGION` environment variable


<a id="nestedatt--assume_role"></a>

### Nested Schema for `assume_role`

Required:

- `assumeRoleTrn` (String) he TRN of the role to assume.
- `durationSeconds` (Number) The duration of the session when making the AssumeRole call. Its value ranges from 900 to 43200(seconds), and default is 3600 seconds.
  Optional:

- `policy` (String) A more restrictive policy when making the AssumeRole call

<a id="nestedatt--endpoints"></a>

### Nested Schema for `endpoints`

Optional:

- `cloudcontrolapi` (String) Use this to override the default Cloud Control API service endpoint URL
- `sts` (String) Use this to override the default STS service endpoint URL