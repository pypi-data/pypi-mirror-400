# TAXII® Version 2.0
## Committee Specification 01
**Date:** 19 July 2017

---

## Specification URIs

### This version:
- [taxii-v2.0-cs01.docx](http://docs.oasis-open.org/cti/taxii/v2.0/cs01/taxii-v2.0-cs01.docx) (Authoritative)
- [taxii-v2.0-cs01.html](http://docs.oasis-open.org/cti/taxii/v2.0/cs01/taxii-v2.0-cs01.html)
- [taxii-v2.0-cs01.pdf](http://docs.oasis-open.org/cti/taxii/v2.0/cs01/taxii-v2.0-cs01.pdf)

### Previous version:
- [taxii-v2.0-csprd01.docx](http://docs.oasis-open.org/cti/taxii/v2.0/csprd01/taxii-v2.0-csprd01.docx) (Authoritative)
- [taxii-v2.0-csprd01.html](http://docs.oasis-open.org/cti/taxii/v2.0/csprd01/taxii-v2.0-csprd01.html)
- [taxii-v2.0-csprd01.pdf](http://docs.oasis-open.org/cti/taxii/v2.0/csprd01/taxii-v2.0-csprd01.pdf)

### Latest version:
- [taxii-v2.0.docx](http://docs.oasis-open.org/cti/taxii/v2.0/taxii-v2.0.docx) (Authoritative)
- [taxii-v2.0.html](http://docs.oasis-open.org/cti/taxii/v2.0/taxii-v2.0.html)
- [taxii-v2.0.pdf](http://docs.oasis-open.org/cti/taxii/v2.0/taxii-v2.0.pdf)

---

## Technical Committee
**OASIS Cyber Threat Intelligence (CTI) TC**
- [CTI TC Homepage](https://www.oasis-open.org/committees/cti/)

### Chair
- Richard Struse (Richard.Struse@hq.dhs.gov)
- [DHS Office of Cybersecurity and Communications (CS&C)](http://www.dhs.gov/office-cybersecurity-and-communications)

### Editors
- John Wunder (jwunder@mitre.org) - MITRE Corporation
- Mark Davidson (Mark.Davidson@nc4.com) - NC4
- Bret Jordan (bret_jordan@symantec.com) - Symantec Corp.

---

## Abstract

Trusted Automated eXchange of Intelligence Information (TAXII®) is an application layer protocol for the communication of cyber threat information in a simple and scalable manner. This specification defines the TAXII RESTful API and its resources along with the requirements for TAXII Client and Server implementations.

---

## Status

This document was last revised or approved by the OASIS Cyber Threat Intelligence (CTI) TC on the above date. Check the "Latest version" location noted above for possible later revisions of this document.

For information on patents, intellectual property rights, and other policies, refer to the [OASIS CTI TC IPR page](https://www.oasis-open.org/committees/cti/ipr.php).

---

## Citation Format

When referencing this specification, use the following citation:

**[TAXII-v2.0]** TAXII® Version 2.0. Edited by John Wunder, Mark Davidson, and Bret Jordan. 19 July 2017. OASIS Committee Specification 01. [http://docs.oasis-open.org/cti/taxii/v2.0/cs01/taxii-v2.0-cs01.html](http://docs.oasis-open.org/cti/taxii/v2.0/cs01/taxii-v2.0-cs01.html).

Latest version: [http://docs.oasis-open.org/cti/taxii/v2.0/taxii-v2.0.html](http://docs.oasis-open.org/cti/taxii/v2.0/taxii-v2.0.html).

---

## Notices

Copyright © OASIS Open 2017. All Rights Reserved.

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published, and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this notice are included on all such copies and derivative works.

This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

---

# 1. Introduction

## 1.1 Overview

Trusted Automated Exchange of Intelligence Information (TAXII) is an application layer protocol used to exchange cyber threat intelligence (CTI) over HTTPS. TAXII enables organizations to share CTI by defining an API that aligns with common sharing models.

TAXII defines two primary services:

- **Collections:** Allow a producer to host a set of CTI data that can be requested by consumers
- **Channels:** Allow producers to push data to many consumers and allow consumers to receive data from many producers

Collections and Channels can be organized by grouping them into an API Root to support the needs of a particular trust group or to organize them in some other way.

Note: This version of the TAXII specification reserves the keywords required for Channels but does not specify Channel services. Channels and their services will be defined in a subsequent version of this specification.

## 1.2 STIX Support

TAXII is specifically designed to support the exchange of CTI represented in STIX. The examples and some features in the specification are intended to align with STIX. However, TAXII is not limited to STIX and can be used to share data in other formats.

## 1.3 Discovery Methods

This specification defines two discovery methods:

### 1.3.1 DNS SRV Record Discovery

A network level discovery method that uses a DNS SRV record (RFC 2782) to advertise the location of a TAXII Server within a network or to the general Internet. This allows TAXII-enabled security infrastructure to automatically locate an organization's internal TAXII Server. See section 3.9 for complete information on advertising TAXII Servers in DNS.

### 1.3.2 Discovery Endpoint

A Discovery Endpoint enables authorized clients to obtain information about a TAXII Server and get a list of API Roots. See section 4.1 for complete information on the Discovery Endpoint.

## 1.4 TAXII Components

### 1.4.1 API Roots

API Roots are logical groupings of TAXII Channels, Collections, and related functionality. A TAXII server instance can support one or more API Roots. API Roots can be thought of as instances of the TAXII API available at different URLs, where each API Root is the "root" URL of that particular instance of the TAXII API.

Organizing the Channels and Collections into API Roots allows for a division of content and access control by trust group or any other logical grouping. For example, a single TAXII Server could host multiple API Roots - one for Sharing Group A and another for Sharing Group B.

### 1.4.2 Endpoints

An Endpoint consists of a specific URL and HTTP Method on a TAXII Server that a TAXII Client can contact to engage in one specific type of TAXII exchange. For example, each Collection on a TAXII Server has an Endpoint that can be used to get information about it.

### 1.4.3 Collections

A TAXII Collection is an interface to a logical repository of CTI objects provided by a TAXII Server. Collections are used by TAXII Clients to send information to the TAXII Server or request information from the TAXII Server. A TAXII Server can host multiple Collections per API Root, and Collections are used to exchange information in a request-response manner.

### 1.4.4 Channels

A TAXII Channel is maintained by a TAXII Server and enables TAXII Clients to exchange information with other TAXII Clients in a publish-subscribe model. TAXII Clients can publish messages to Channels and subscribe to Channels to receive published messages.

### 1.4.5 Transport Protocol

The TAXII protocol defined in this specification uses HTTPS (HTTP over TLS) as the transport for all communications.

## 1.5 HTTP Content Negotiation

This specification uses HTTP content negotiation (RFC 7231).

### Supported Media Types

| Media Type | Description |
|---|---|
| application/vnd.oasis.taxii+json | Any version of TAXII in JSON |
| application/vnd.oasis.taxii+json; version=2.0 | TAXII version 2.0 in JSON |
| application/vnd.oasis.stix+json | Any version of STIX in JSON |
| application/vnd.oasis.stix+json; version=2.0 | STIX version 2.0 in JSON |

## 1.6 Authentication and Authorization

### Overview

Access control to an instance of the TAXII API is specific to the sharing community, vendor, or product and is not defined by this specification.

Authentication and Authorization in TAXII is implemented as defined in RFC 7235, using the Authorization and WWW-Authenticate HTTP headers respectively.

### HTTP Basic Authentication

HTTP Basic authentication, as defined in RFC 7617, is the mandatory-to-implement authentication scheme in TAXII. TAXII Servers and Clients are required to implement support for HTTP Basic, though other authentication schemes can also be supported. Implementers can allow operators to disable the use of HTTP Basic in their operations.

### Authentication Response

If the TAXII Server receives a request for any Endpoint that requires authentication and either an acceptable Authorization header is not sent or the server does not determine that the client is authorized, the server responds with HTTP 401 (Unauthorized) status code and a WWW-Authenticate HTTP header.

## 1.7 STIX and Other Content

TAXII is designed with STIX in mind and support for exchanging STIX 2.0 content is mandatory to implement. Additional content types are permitted, but specific requirements for STIX are present throughout the document.

---

# 2. Data Types

This section defines the names and permitted values of common types used throughout this specification.

| Type | Description |
|---|---|
| api-root | An API Root Resource |
| boolean | A value of either true or false |
| bundle | A STIX Bundle |
| collection | A Collection Resource |
| collections | A Collections Resource |
| dictionary | A JSON object that captures an arbitrary set of key/value pairs |
| discovery | A Discovery Resource |
| error | An Error Message |
| identifier | An RFC 4122-compliant Version 4 UUID |
| integer | A whole number, signed 64-bit value |
| list | A sequence of values ordered based on how they appear in the list |
| manifest | A Manifest Resource |
| object | An Object Resource |
| status | A Status Resource |
| string | A finite-length string of valid Unicode characters |
| timestamp | Represented in RFC 3339 format, UTC timezone, with 'Z' designation |

---

# 3. TAXII API - Core Concepts

## 3.1 Endpoints Summary

| URL | Methods | Resource Type |
|---|---|---|
| /taxii/ | GET | discovery |
| <api-root>/ | GET | api-root |
| <api-root>/status/<status-id>/ | GET | status |
| <api-root>/collections/ | GET | collections |
| <api-root>/collections/<id>/ | GET | collection |
| <api-root>/collections/<id>/objects/ | GET, POST | object |
| <api-root>/collections/<id>/objects/<object-id>/ | GET | object |
| <api-root>/collections/<id>/manifest/ | GET | manifest |

## 3.2 HTTP Headers

### Standard Headers

| Header | Description |
|---|---|
| Accept | Specifies which Content-Types are acceptable in response |
| Accept-Ranges | Indicates acceptance of range requests for a resource |
| Authorization | Specifies authentication credentials |
| Content-Range | Identifies which subrange(s) of a resource are in an HTTP 206 response |
| Content-Type | Identifies the format of HTTP Requests and Responses |
| Range | Requests a subrange of a resource |
| WWW-Authenticate | Indicates authentication is required and specifies supported schemes |

### Custom Headers

| Header | Description |
|---|---|
| X-TAXII-Date-Added-First | Indicates the date_added timestamp of the first object in the response |
| X-TAXII-Date-Added-Last | Indicates the date_added timestamp of the last object in the response |

## 3.3 Sorting

For Collections and Manifest Endpoints, objects MUST be sorted in ascending order by the date the object first appeared in the TAXII Collection (the added date). The most recently added object is last in the list.

For the Collections Endpoint, Collections MUST be sorted consistently across responses to support pagination.

## 3.4 Pagination

### Overview

Pagination is a feature used to break up result sets over multiple request/response pairs. TAXII uses HTTP's Range and Content-Range headers and defines the items range unit.

### Range Unit: items

The items range unit is defined for expressing subranges of a resource. For Endpoints that return objects, items represents objects. For Endpoints that return collections, items represents Collections.

The first items value gives the first item in a range. The last items value gives the last item; items ranges are inclusive. Items are zero-indexed (the first item is object zero).

### Supported Endpoints for Pagination

- GET <api-root>/collections/
- GET <api-root>/collections/<id>/objects/
- GET <api-root>/collections/<id>/manifest/

### Pagination Requirements

- The Accept-Ranges header MUST contain items as an acceptable range for resources supporting items-based pagination
- Requests MAY use the Range header to request a subset of data
- HTTP 206 (Partial Content) responses include a Content-Range header
- If the requested Range cannot be satisfied, HTTP 416 (Requested Range Not Satisfiable) is used
- An HTTP 206 response MAY be returned even if the original request did not have a Range header
- Responses to requests with a Range header SHOULD contain only the requested range

### Example: Pagination Usage

**Request without Range header:**
```
GET .../collections/my-collection/objects/?added_after=2016-02-01T00:00:01.000Z HTTP/1.1
Accept: application/vnd.oasis.stix+json; version=2.0
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/vnd.oasis.stix+json; version=2.0
```

**Request with Range header (items 0-49):**
```
GET .../collections/my-collection/objects/?added_after=2016-02-01T00:00:01.000Z HTTP/1.1
Range: items 0-49
Accept: application/vnd.oasis.stix+json; version=2.0
```

**Response:**
```
HTTP/1.1 206 Partial Content
Content-Type: application/vnd.oasis.stix+json; version=2.0
X-TAXII-Date-Added-First=2016-02-21T05:01:01.000Z
X-TAXII-Date-Added-Last=2016-02-21T12:01:01.000Z
Content-Range: items 0-49/500
```

## 3.5 Filtering

### Overview

A TAXII Client may request specific content from a TAXII Server by specifying a set of filters in the request. If no filter parameters are specified, the TAXII Client is requesting all content be returned for that Endpoint.

### URL Parameters

#### added_after

A timestamp that filters objects to only include those added to the Channel or Collection after the specified timestamp. The added_after parameter is not related to dates or times within a STIX object.

Note: The HTTP Date header can be used to identify and correct any time skew between client and server.

#### match[<field>]

The match parameter defines filtering on the specified field. Each field MUST NOT occur more than once in a request. Each match MAY contain one or more values separated by commas without spaces. Multiple values are treated as a logical OR.

Examples:
- `?match[type]=incident,ttp,actor`
- `?match[type]=incident&match[version]=2016-01-01T01:01:01.000Z`

### Match Fields

| Field | Description |
|---|---|
| id | The identifier of the object(s) being requested (STIX ID for STIX objects) |
| type | The type of object(s) being requested |
| version | The version of object(s) being requested |

### Version Parameter Values

- `last` - requests the latest version of an object (default)
- `first` - requests the earliest version of an object
- `all` - requests all versions of an object
- `<value>` - requests a specific version of an object

## 3.6 Error Handling

### Overview

TAXII primarily relies on standard HTTP error semantics (400-series and 500-series status codes) to indicate when an error has occurred. TAXII also defines an error message structure provided in the response body when an error status is returned.

### Error Message Resource

The error message is provided by TAXII Servers in the response body when returning an HTTP error status and contains more information describing the error.

| Property | Type | Description |
|---|---|---|
| title | string | A human-readable plain text title for this error (required) |
| description | string | A human-readable plain text description of the error (optional) |
| error_id | string | An identifier for this particular error instance (optional) |
| error_code | string | The error code for this error type (optional) |
| http_status | string | The HTTP status code applicable to this error (optional) |
| external_details | string | A URL pointing to additional details (optional) |
| details | dictionary | Additional server-specific details about the error (optional) |

### Example Error Response

```json
{
  "title": "Error condition XYZ",
  "description": "This error is caused when the application tries to access data...",
  "error_id": "1234",
  "error_code": "581234",
  "http_status": "409",
  "external_details": "http://example.com/ticketnumber1/errorid-1234",
  "details": {
    "somekey1": "somevalue",
    "somekey2": "some other value"
  }
}
```

## 3.7 Object Resource

### Overview

This resource type is negotiated based on the media type. This specification does not define any form of content wrapper for objects. Instead, objects are the direct payload of HTTP messages.

### STIX Content Delivery

When returning STIX 2.0 content in a TAXII response, the root object MUST be a STIX bundle per STIX 2.0 specification. Examples include:

- A single indicator in response to a request for an indicator by ID is enclosed in a bundle
- A list of campaigns returned from a Collection is enclosed in a bundle
- An empty response with no STIX objects results in an empty bundle

### Example STIX Bundle Response

```json
{
  "type": "bundle",
  "objects": [
    {
      "type": "indicator",
      "id": "indicator--252c7c11-daf2-42bd-843b-be65edca9f61"
    }
  ]
}
```

## 3.8 JSON Serialization Requirements

- All property names and string literals MUST be exactly the same, including case, as specified in this document
- Properties marked required in the property tables MUST be present in the JSON serialization of that resource
- Example: The discovery resource has a property called api_roots which must result in the JSON key name "api_roots"

## 3.9 DNS SRV Record for TAXII Server Discovery

Organizations implementing a DNS SRV record to advertise the location of their TAXII Server MUST use the service name taxii.

### Example DNS SRV Record

```
_taxii._tcp.example.com. 86400 IN SRV 0 5 443 taxii-hub-1.example.com
```

This example advertises a TAXII Server for the domain "example.com" located at taxii-hub-1.example.com:443.

---

# 4. TAXII API - Server Information

## 4.1 Discovery Endpoint

### Overview

This Endpoint provides general information about a TAXII Server, including the advertised API Roots. It's a common entry point for TAXII Clients into the data and services provided by a TAXII Server.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /taxii/ |
| Parameters | N/A |
| Pagination | No |
| Filtering | No |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Content-Type: application/vnd.oasis.taxii+json; version=2.0 |
| Common Error Codes | 404, 401, 403 |

### Discovery Resource

The discovery resource contains information about a TAXII Server.

| Property | Type | Description |
|---|---|---|
| title | string | A human-readable name for this server (required) |
| description | string | A human-readable description for this server (optional) |
| contact | string | Contact information for the server administrator (optional) |
| default | string | The default API Root that a TAXII Client MAY use (optional) |
| api_roots | list of string | A list of URLs that identify known API Roots (optional) |

### Example Request and Response

**Request:**
```
GET /taxii/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.taxii+json; version=2.0
```

**Response:**
```json
{
  "title": "Some TAXII Server",
  "description": "This TAXII Server contains a listing of...",
  "contact": "string containing contact information",
  "default": "https://example.com/api2/",
  "api_roots": [
    "https://example.com/api1/",
    "https://example.com/api2/",
    "https://example.net/trustgroup1/"
  ]
}
```

## 4.2 API Root Endpoint

### Overview

This Endpoint provides general information about an API Root, which can be used to help users and clients decide whether and how they want to interact with it.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/ |
| Parameters | <api-root> - the base URL of the API Root |
| Pagination | No |
| Filtering | No |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Content-Type: application/vnd.oasis.taxii+json; version=2.0 |
| Common Error Codes | 404, 401, 403 |

### API Root Resource

The api-root resource contains general information about the API Root.

| Property | Type | Description |
|---|---|---|
| title | string | A human-readable name for this API instance (required) |
| description | string | A human-readable description for this API Root (optional) |
| versions | list of string | List of TAXII versions this API Root is compatible with (required) |
| max_content_length | integer | Maximum size of request body in bytes (required) |

### Example Request and Response

**Request:**
```
GET /api1/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.taxii+json; version=2.0
```

**Response:**
```json
{
  "title": "Malware Research Group",
  "description": "A trust group setup for malware researchers",
  "versions": ["taxii-2.0"],
  "max_content_length": 9765625
}
```

## 4.3 Status Endpoint

### Overview

This Endpoint provides information about the status of a previous request. In TAXII 2.0, the only request that can be monitored is one to add objects to a Collection. It is typically used by TAXII Clients to monitor a request they made to take action when it is complete.

TAXII Servers SHOULD provide status messages at this Endpoint while the request is in progress until at least 24 hours after it has been marked completed.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/status/<status-id>/ |
| Parameters | <api-root>, <status-id> |
| Pagination | No |
| Filtering | No |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Content-Type: application/vnd.oasis.taxii+json; version=2.0 |
| Common Error Codes | 404, 401, 403 |

### Status Resource

The status resource represents information about a request to add objects to a Collection.

| Property | Type | Description |
|---|---|---|
| id | string | The identifier of this Status resource (required) |
| status | string | Overall status - either "complete" or "pending" (required) |
| request_timestamp | timestamp | The datetime of the request being monitored (optional) |
| total_count | integer | Total number of objects in the request (required) |
| success_count | integer | Number of objects successfully created (required) |
| successes | list of string | List of object IDs that were successfully processed (optional) |
| failure_count | integer | Number of objects that failed to be created (required) |
| failures | list of status-failure | List of objects that were not successfully processed (optional) |
| pending_count | integer | Number of objects yet to be processed (required) |
| pendings | list of string | List of objects that have yet to be processed (optional) |

### Status Failure Type

| Property | Type | Description |
|---|---|---|
| id | string | The identifier of the object that failed (required) |
| message | string | Message indicating why the object failed (optional) |

### Example Response

```json
{
  "id": "2d086da7-4bdc-4f91-900e-d77486753710",
  "status": "pending",
  "request_timestamp": "2016-11-02T12:34:34.12345Z",
  "total_count": 4,
  "success_count": 1,
  "successes": [
    "indicator--c410e480-e42b-47d1-9476-85307c12bcbf"
  ],
  "failure_count": 1,
  "failures": [
    {
      "id": "malware--664fa29d-bf65-4f28-a667-bdb76f29ec98",
      "message": "Unable to process object"
    }
  ],
  "pending_count": 2,
  "pendings": [
    "indicator--252c7c11-daf2-42bd-843b-be65edca9f61",
    "relationship--045585ad-a22f-4333-af33-bfd503a683b5"
  ]
}
```

---

# 5. TAXII API - Collections

## 5.1 Collections Endpoint

### Overview

This Endpoint provides information about the Collections hosted under an API Root. It provides the Collection's id, which is used to request objects or manifest entries from the Collection.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/collections/ |
| Parameters | <api-root> |
| Pagination | Yes |
| Filtering | No |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Body: collections |
| Common Error Codes | 404, 401, 403 |

### Collections Resource

The collections resource is a simple wrapper around a list of collection resources.

| Property | Type | Description |
|---|---|---|
| collections | list of collection | A list of Collections (optional) |

### Example Request and Response

**Request:**
```
GET /api1/collections/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.taxii+json; version=2.0
```

**Response:**
```json
{
  "collections": [
    {
      "id": "91a7b528-80eb-42ed-a74d-c6fbd5a26116",
      "title": "High Value Indicator Collection",
      "description": "This data collection is for collecting high value IOCs",
      "can_read": true,
      "can_write": false,
      "media_types": [
        "application/vnd.oasis.stix+json; version=2.0"
      ]
    },
    {
      "id": "52892447-4d7e-4f70-b94d-d7f22742ff63",
      "title": "Indicators from the past 24-hours",
      "description": "This data collection is for collecting current IOCs",
      "can_read": true,
      "can_write": false,
      "media_types": [
        "application/vnd.oasis.stix+json; version=2.0"
      ]
    }
  ]
}
```

## 5.2 Collection Endpoint

### Overview

This Endpoint provides general information about a Collection.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/collections/<id>/ |
| Parameters | <api-root>, <id> |
| Pagination | No |
| Filtering | No |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Body: collection |
| Common Error Codes | 404, 401, 403 |

### Collection Resource

The collection resource contains general information about a Collection.

| Property | Type | Description |
|---|---|---|
| id | identifier | Universally unique identifier for this Collection (required) |
| title | string | A human-readable name for this Collection (required) |
| description | string | A human-readable description (optional) |
| can_read | boolean | Indicates if the requester can read objects from this Collection (required) |
| can_write | boolean | Indicates if the requester can write objects to this Collection (required) |
| media_types | list of string | List of supported media types for objects (optional) |

### Example Request and Response

**Request:**
```
GET /api1/collections/91a7b528-80eb-42ed-a74d-c6fbd5a26116/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.taxii+json; version=2.0
```

**Response:**
```json
{
  "id": "91a7b528-80eb-42ed-a74d-c6fbd5a26116",
  "title": "High Value Indicator Collection",
  "description": "This data collection is for collecting high value IOCs",
  "can_read": true,
  "can_write": false,
  "media_types": [
    "application/vnd.oasis.stix+json; version=2.0"
  ]
}
```

## 5.3 Get Objects Endpoint

### Overview

This Endpoint retrieves objects from a Collection. Clients can search for objects, retrieve all objects, or paginate through objects.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/collections/<id>/objects/ |
| Parameters | <api-root>, <id> |
| Pagination | Yes |
| Filtering | Yes - id, type, version |
| Valid Request Type | Accept: application/vnd.oasis.stix+json; version=2.0 |
| Successful Response | Status: 200 (OK), Body: bundle |
| Common Error Codes | 404, 401, 403 |

### Example Request and Response

**Request:**
```
GET /api1/collections/91a7b528-80eb-42ed-a74d-c6fbd5a26116/objects/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.stix+json; version=2.0
```

**Response:**
```json
{
  "type": "bundle",
  "objects": [
    {
      "type": "indicator"
    }
  ]
}
```

## 5.4 Add Objects Endpoint

### Overview

This Endpoint adds objects to a Collection.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | POST |
| URL | /<api-root>/collections/<id>/objects/ |
| Parameters | <api-root>, <id> |
| Pagination | No |
| Filtering | No |
| Valid Request Type | Content-Type: application/vnd.oasis.stix+json; version=2.0 |
| Successful Response | Status: 202 (Accepted), Body: status |
| Common Error Codes | 422, 401, 403 |

### Example Request and Response

**Request:**
```
POST /api1/collections/91a7b528-80eb-42ed-a74d-c6fbd5a26116/objects/ HTTP/1.1
Host: example.com
Accept: application/vnd.oasis.taxii+json; version=2.0
Content-Type: application/vnd.oasis.stix+json; version=2.0

{
  "type": "bundle",
  "objects": [
    {
      "type": "indicator",
      "id": "indicator--c410e480-e42b-47d1-9476-85307c12bcbf"
    }
  ]
}
```

**Response:**
```json
{
  "id": "2d086da7-4bdc-4f91-900e-d77486753710",
  "status": "pending",
  "request_timestamp": "2016-11-02T12:34:34.12345Z",
  "total_count": 4,
  "success_count": 1,
  "successes": [
    "indicator--c410e480-e42b-47d1-9476-85307c12bcbf"
  ],
  "failure_count": 0,
  "pending_count": 3
}
```

## 5.5 Get Object by ID Endpoint

### Overview

This Endpoint gets an object from a Collection by its id.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/collections/<id>/objects/<object-id>/ |
| Parameters | <api-root>, <id>, <object-id> |
| Pagination | No |
| Filtering | Yes - version |
| Valid Request Type | Accept: application/vnd.oasis.stix+json; version=2.0 |
| Successful Response | Status: 200 (OK), Body: bundle |
| Common Error Codes | 404, 401, 403 |

## 5.6 Manifest Endpoint

### Overview

This Endpoint retrieves a manifest about objects from a Collection. Instead of returning objects, it returns metadata about objects.

### Endpoint Specification

| Property | Value |
|---|---|
| Supported Method | GET |
| URL | /<api-root>/collections/<id>/manifest/ |
| Parameters | <api-root>, <id> |
| Pagination | Yes |
| Filtering | Yes - id, type, version |
| Valid Request Type | Accept: application/vnd.oasis.taxii+json; version=2.0 |
| Successful Response | Status: 200 (OK), Body: manifest |
| Common Error Codes | 404, 401, 403 |

### Manifest Resource

The manifest resource is a wrapper around a list of manifest-entry items.

| Property | Type | Description |
|---|---|---|
| objects | list of manifest-entry | List of manifest entries (optional) |

### Manifest Entry Type

| Property | Type | Description |
|---|---|---|
| id | identifier | The identifier of the object (required) |
| date_added | timestamp | When the object was added to the server (optional) |
| versions | list of string | Available versions, sorted most recent first (optional) |
| media_types | list of string | Media types this object can be requested in (optional) |

### Example Response

```json
{
  "objects": [
    {
      "id": "indicator--29aba82c-5393-42a8-9edb-6a2cb1df070b",
      "date_added": "2016-11-01T03:04:05Z",
      "versions": [
        "2016-11-03T12:30:59.000Z",
        "2016-12-03T12:30:59.000Z"
      ],
      "media_types": [
        "application/vnd.oasis.stix+json; version=2.0"
      ]
    },
    {
      "id": "indicator--ef0b28e1-308c-4a30-8770-9b4851b260a5",
      "date_added": "2016-11-01T10:29:05Z",
      "versions": [
        "2016-11-03T12:30:59.000Z"
      ],
      "media_types": [
        "application/vnd.oasis.stix+json; version=2.0"
      ]
    }
  ]
}
```

---

# 6. Customizing TAXII Resources

## 6.1 Custom Properties

It is understood that there will be cases where certain information exchanges can be improved by adding properties that are not specified in this document. These properties are called Custom Properties.

### Rules for Custom Properties

- A TAXII resource MAY have any number of Custom Properties
- Custom Property names MUST be in ASCII and limited to lowercase letters (a-z) and underscore (_)
- Custom Property names SHOULD start with "x_" followed by a source unique identifier (like a domain name), an underscore and then the name (e.g., x_examplecom_customfield)
- Custom Property names SHOULD be no longer than 30 ASCII characters
- Custom Property names MUST have a minimum length of 3 ASCII characters
- Custom Property names MUST be no longer than 256 ASCII characters
- Custom Property names not prefixed with "x_" may be used in future versions of the specification
- Custom Property names SHOULD be unique when produced by the same source
- Custom Properties SHOULD only be used when no existing TAXII properties fulfill that need

### Server Handling of Custom Properties

TAXII Servers that receive a TAXII Resource with unrecognized Custom Properties MAY respond in one of two ways:

1. Refuse to process the content and respond with HTTP 422 (Unprocessable Entity)
2. Silently ignore non-understood properties and continue processing

### Client Handling of Custom Properties

TAXII Clients that receive a TAXII Resource with unrecognized Custom Properties MAY silently ignore non-understood properties and continue processing.

### Example Custom Property

```json
{
  "x_acmeinc_scoring": {
    "impact": "high",
    "probability": "low"
  }
}
```

---

# 7. TAXII Server Implementation

## 7.1 TAXII Server Types

A "TAXII 2.0 Server" is any software that conforms to the requirements for a TAXII Collections Server as defined in section 7.2.

## 7.2 TAXII 2.0 Collections Server

A "TAXII 2.0 Collections Server" is any software that conforms to the following requirements:

- It MUST support all requirements in sections 3, 4, and 5
- It MUST include all required properties within TAXII Resources
- It MUST support all features listed in section 7.3 (Mandatory Server Features)
- It MAY support any features listed in section 7.4 (Optional Server Features)

## 7.3 Mandatory Server Features

### Core Server Requirements

1. MUST define the URL of the Discovery API to be `/taxii/` at the root of the server (e.g., `https://example.com/taxii/`)
2. MUST support at least one API Root
3. MAY support multiple API Roots
4. MAY implement other HTTP Methods, Content Types, and/or URLs beyond those defined in this specification
5. MUST be capable of sending HTTP responses for features it supports with valid TAXII or STIX content
6. All properties MUST conform to the data type and normative requirements specified

### HTTPS and Authentication Server Requirements

1. MUST accept TAXII 2.0 requests using HTTPS
2. MUST accept connections using TLS version 1.2 and SHOULD accept TLS version 1.3 or higher
3. SHOULD NOT accept TLS 1.2 connections using cipher suites listed in the RFC 7540 blacklist
4. MUST implement HTTP Basic authentication scheme per RFC 7617
5. MAY permit configurations that enable/disable all authentication schemes
6. MAY implement additional authentication and authorization schemes
7. MAY restrict access by omitting specific objects or fields from responses
8. MAY permit operators to disable all authentication
9. MAY choose not to respond to unauthorized requests

## 7.4 Optional Server Features

### Client Certificate Verification

TAXII 2.0 servers MAY choose to verify a client's certificate for authentication. Servers supporting this feature MUST follow these requirements:

- The default strategy SHOULD be PKIX as defined in RFC 5280, RFC 6818, RFC 6125, et al.
- MAY support other certificate verification policies such as Certificate Pinning

---

# 8. TAXII Client Implementation

## 8.1 TAXII Client Types

A "TAXII 2.0 Client" is any software that conforms to the requirements for a TAXII Collections Client as defined in section 8.2.

## 8.2 TAXII 2.0 Collections Client

A "TAXII 2.0 Collections Client" is any software that exchanges CTI data with a TAXII 2.0 Collections Server. It must conform to:

- SHOULD be capable of looking up and using the TAXII SRV record from DNS
- MUST support parsing all properties for resources in sections 4 and 5
- MUST support all features listed in section 8.3 (Mandatory Client Features)

## 8.3 Mandatory Client Features

### HTTPS and Authentication Client Requirements

1. MUST initiate TAXII 2.0 requests using HTTPS
2. MUST support TLS 1.2 and SHOULD use TLS 1.3 or higher
3. SHOULD NOT use TLS 1.2 with cipher suites listed in RFC 7540 blacklist
4. MUST implement HTTP Basic authentication scheme as a client per RFC 7617
5. MAY implement additional authentication schemes

### Server Certificate Verification

- The default strategy SHOULD be PKIX as defined in RFC 5280, RFC 6818, RFC 6125, et al.
- MAY support other certification verification policies:
  - **Certificate Pinning:** Hard-coded or distributed pinned certificate authorities or end-entity certificates
  - **DANE:** DNS-based Authentication of Named Entities (RFC 7671) - Systems implementing DANE SHOULD also implement DNSSEC (RFC 4033)
  - **Self-Signed Certificates:** MAY be supported via Certificate Pinning and/or DANE

---

# 9. Glossary

**API Root** - A grouping of TAXII Channels, Collections, and related functionality.

**Channel** - A publish-subscribe communications method where messages are exchanged.

**CTI** - Cyber Threat Intelligence

**Collection** - A logical group of CTI objects.

**Endpoint** - A combination of a URL and HTTP method with defined behavior in TAXII.

**STIX** - Structured Threat Information Expression (STIX®) is a language and serialization format used to exchange cyber threat intelligence (CTI).

**STIX Content** - STIX documents, including STIX Objects, grouped as STIX Bundles.

**STIX Object** - A STIX Domain Object (SDO) or STIX Relationship Object (SRO).

**TAXII** - Trusted Automated eXchange of Intelligence Information (TAXII®) is an application layer protocol for the communication of cyber threat intelligence (CTI).

**TAXII Client** - A software package that connects to a TAXII Server and supports the exchange of CTI.

**TAXII Server** - A software package that supports the exchange of CTI.

---

# 10. References

## Normative References

- **[HTTP Auth]** - IANA, "Hypertext Transfer Protocol (HTTP) Authentication Scheme Registry", March 2017. Available: https://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml

- **[ISO10646]** - ISO/IEC 10646:2014 Information technology -- Universal Coded Character Set (UCS), 2014.

- **[RFC0020]** - Cerf, V., "ASCII format for network interchange", STD 80, RFC 20, October 1969.

- **[RFC2119]** - Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.

- **[RFC2782]** - Gulbrandsen, A., Vixie, P., and L. Esibov, "A DNS RR for specifying the location of services (DNS SRV)", RFC 2782, February 2000.

- **[RFC3339]** - Klyne, G. and C. Newman, "Date and Time on the Internet: Timestamps", RFC 3339, July 2002.

- **[RFC4033]** - Arends, R., Austein, R., Larson, M., Massey, D., and S. Rose, "DNS Security Introduction and Requirements", RFC 4033, March 2005.

- **[RFC4122]** - Leach, P., Mealling, M., and R. Salz, "A Universally Unique IDentifier (UUID) URN Namespace", RFC 4122, July 2005.

- **[RFC5246]** - Dierks, T. and E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.2", RFC 5246, August 2008.

- **[RFC5280]** - Cooper, D., Santesson, S., Farrell, S., Boeyen, S., Housley, R., and W. Polk, "Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile", RFC 5280, May 2008.

- **[RFC6125]** - Saint-Andre, P. and J. Hodges, "Representation and Verification of Domain-Based Application Service Identity within Internet Public Key Infrastructure Using X.509 (PKIX) Certificates in the Context of Transport Layer Security (TLS)", RFC 6125, March 2011.

- **[RFC6818]** - Yee, P., "Updates to the Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile", RFC 6818, January 2013.

- **[RFC7230]** - Fielding, R., Ed., and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Message Syntax and Routing", RFC 7230, June 2014.

- **[RFC7231]** - Fielding, R., Ed., and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content", RFC 7231, June 2014.

- **[RFC7233]** - Fielding, R., Ed., Y. Lafon, Ed., and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Range Requests", RFC 7233, June 2014.

- **[RFC7235]** - Fielding, R., Ed., and J. Reschke, Ed., "Hypertext Transfer Protocol (HTTP/1.1): Authentication", RFC 7235, June 2014.

- **[RFC7540]** - Belshe, M., Peon, R., and M. Thomson, Ed., "Hypertext Transfer Protocol Version 2 (HTTP/2)", RFC 7540, May 2015.

- **[RFC7617]** - Reschke, J., "The 'Basic' HTTP Authentication Scheme", RFC 7617, September 2015.

- **[RFC7671]** - Dukhovni, V. and W. Hardaker, "The DNS-Based Authentication of Named Entities (DANE) Protocol: Updates and Operational Guidance", RFC 7671, October 2015.

- **[TLS1.3]** - Rescorla, E., "The Transport Layer Security (TLS) Protocol Version 1.3 draft-ietf-tls-tls13-20", RFC draft. Available: https://tools.ietf.org/html/draft-ietf-tls-tls13-20

---

## Editors and Contributors

### Editors
- Bret Jordan, Symantec Corp.
- Mark Davidson, NC4

### Substantial Contributors
- Jane Ginn, Cyber Threat Intelligence Network, Inc. (CTIN)
- Richard Struse, DHS Office of Cybersecurity and Communications
- Sergey Polzunov, EclecticIQ
- Iain Brown, GDS
- Eric Burger, Georgetown University
- Jason Keirstead, IBM
- Allan Thomson, LookingGlass Cyber
- Rich Piazza, MITRE Corporation
- Charles Schmidt, MITRE Corporation
- John Wunder, MITRE Corporation

---

**Document Version:** 01  
**Date:** 2017-04-24  
**Editors:** Bret Jordan, Mark Davidson, John Wunder

---