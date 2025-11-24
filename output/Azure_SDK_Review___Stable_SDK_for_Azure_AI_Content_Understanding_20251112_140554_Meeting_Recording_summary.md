# API/SDK Design Guidelines
**Extracted from:** Azure SDK Review - [Stable SDK for Azure AI Content Understanding]-20251112_140554-Meeting Recording.mp4

> This document contains reusable API/SDK design principles and best practices extracted from technical review meetings.
> These guidelines can be used by developers and LLMs to review APIs or design better SDKs.

**Total Topics:** 25
**Total Design Guidelines:** 18

---

## Segment 1: Meeting Opening and Participant Introduction
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 2: API Review Preparation
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 3: Python and .NET SDK Preview Discussion
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 4: Documentation and Internal Review
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 5: API Design and Implementation Discussion
**Time Range:** 00:12:46.000 - 00:15:08.875
**Total Knowledge Items:** 1

### Design Guideline 1: Designing Flexible Input Handling in APIs
**Source Discussion Time:** 00:12:46.000 - 00:15:08.875
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:13:32.500
<img src="keyframes/segment_5_guideline_1_00-13-32-500.png" alt="Key Frame at 00:13:32.500" width="600"/>

**Problem:**
APIs often require handling various input types, such as single files or multiple documents. A common issue arises when APIs are designed to accept only a single input type, limiting their flexibility and future scalability. For example, an API method like 'def analyze_document(url: str)' restricts input to a single URL, which can be problematic when future requirements demand processing multiple documents simultaneously. This limitation can hinder the API's ability to adapt to evolving user needs and complicate integration with systems that generate multiple outputs.

**Best Practice:**
To enhance flexibility, design APIs to accept input arrays or collections, allowing for multiple inputs. For instance, refactor the method to 'def analyze_documents(urls: List[str])', enabling the processing of multiple URLs. This approach improves scalability and future-proofs the API against evolving requirements. It also simplifies integration with systems that produce multiple outputs. Consider alternative designs like accepting input streams or objects for more complex scenarios. Apply this pattern when designing APIs expected to handle diverse input types or when future expansion is anticipated.

---

## Segment 6: Advanced API Functionality and Invoice Extraction
**Time Range:** 00:15:04.320 - 00:17:17.125
**Total Knowledge Items:** 2

### Design Guideline 1: Advanced Document Layout Analysis
**Source Discussion Time:** 00:15:04.320 - 00:15:30.480
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:15:10.750
<img src="keyframes/segment_6_guideline_1_00-15-10-750.png" alt="Key Frame at 00:15:10.750" width="600"/>

**Problem:**
APIs often provide basic content extraction but lack advanced layout analysis capabilities. This can lead to difficulties in processing complex documents like PDFs with tables. Developers may struggle to accurately extract and utilize table data due to insufficient API support for layout-specific features, such as determining the position of table cells within a document.

**Best Practice:**
Enhance API functionality to include advanced layout analysis features. Implement methods to extract table structures, row counts, and cell positions within documents. BEFORE: `def extract_content(doc): return doc.text` AFTER: `def extract_table_structure(doc): return doc.tables` This approach improves document processing accuracy and developer experience by providing detailed layout information.

### Design Guideline 2: Comprehensive Invoice Field Extraction
**Source Discussion Time:** 00:15:46.800 - 00:17:17.125
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:16:05.875
<img src="keyframes/segment_6_guideline_2_00-16-05-875.png" alt="Key Frame at 00:16:05.875" width="600"/>

**Problem:**
Extracting invoice data from documents can be challenging due to varied field types and structures. APIs may not adequately support the extraction of complex data types like arrays or nested fields, leading to incomplete or inaccurate data retrieval. This is problematic in scenarios requiring detailed financial data processing.

**Best Practice:**
Develop APIs with robust field extraction capabilities, supporting diverse data types such as strings, numbers, and arrays. BEFORE: `def extract_invoice_data(doc): return doc.fields` AFTER: `def extract_invoice_fields(doc): return { 'customer_name': doc.fields['name'], 'total': doc.fields['total'], 'items': doc.fields['items'] }` This solution enhances data accuracy and usability by providing structured access to complex field types.

---

## Segment 7: Custom Analyzer Creation and Management
**Time Range:** 00:17:17.125 - 00:25:28.375
**Total Knowledge Items:** 1

### Design Guideline 1: Custom Content Analyzer Design
**Source Discussion Time:** 00:17:17.125 - 00:25:28.375
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:18:12.250
<img src="keyframes/segment_7_guideline_1_00-18-12-250.png" alt="Key Frame at 00:18:12.250" width="600"/>

**Problem:**
Creating custom analyzers for specific content extraction needs can be complex due to varied requirements for schema definitions and model configurations. Developers may face challenges in defining the correct schema and configuring models for optimal content extraction, leading to inefficient or inaccurate analysis results.

**Best Practice:**
Provide a flexible API framework for custom analyzer creation, allowing developers to define schemas and configure models easily. BEFORE: `def create_analyzer(config): pass` AFTER: `def create_custom_analyzer(config, schema): return Analyzer(config, schema)` This solution enhances developer control and accuracy in content extraction by supporting detailed schema definitions and model configurations.

---

## Segment 8: API Result File Handling and Keyframe Extraction
**Time Range:** 00:25:28.375 - 00:27:29.688
**Total Knowledge Items:** 1

### Design Guideline 1: Efficient Keyframe Extraction from Video Analysis
**Source Discussion Time:** 00:25:28.375 - 00:27:29.688
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:25:34.125
<img src="keyframes/segment_8_guideline_1_00-25-34-125.png" alt="Key Frame at 00:25:34.125" width="600"/>

**Problem:**
Extracting keyframes from video analysis can be challenging due to the need for precise operation IDs and handling chunked responses. Developers may struggle with obtaining accurate timestamps and managing large data sets efficiently, leading to potential performance issues and data handling errors.

**Best Practice:**
Implement a robust API method for keyframe extraction that supports operation ID retrieval and efficient data chunking. BEFORE: `def get_keyframe(video): pass` AFTER: `def extract_keyframe(video, operation_id): return KeyframeExtractor(video, operation_id)` This approach ensures accurate timestamp retrieval and efficient data management, improving performance and reliability in video analysis tasks.

---

## Segment 9: API Design and SDK Pattern Discussion
**Time Range:** 00:27:31.125 - 00:28:43.125
**Total Knowledge Items:** 1

### Design Guideline 1: Simplify Client Operations in SDKs
**Source Discussion Time:** 00:27:31.125 - 00:28:43.125
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:27:44.062
<img src="keyframes/segment_9_guideline_1_00-27-44-062.png" alt="Key Frame at 00:27:44.062" width="600"/>

**Problem:**
In many SDKs, operations are nested under a client object, requiring users to navigate through multiple layers to perform a single operation. This pattern can lead to cumbersome code and a steep learning curve for developers unfamiliar with the SDK's structure. For example, a developer might need to call 'client.operation.analyze()' to perform an analysis, which is not intuitive and can lead to errors if the hierarchy is misunderstood.

**Best Practice:**
Promote operations to the client level to simplify the SDK interface. This can be achieved using decorators or similar mechanisms to expose operations directly on the client object. For example, instead of 'client.operation.analyze()', allow 'client.analyze()'. This approach reduces complexity, improves usability, and enhances developer experience by making common operations more accessible. Consider this pattern when designing SDKs with a single or few operations to streamline user interaction.

---

## Segment 10: API Bug and Code Review
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 11: API Design and Copy Authorization
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 12: API Method Consistency and Defaults
**Time Range:** 00:44:38.960 - 00:45:00.080
**Total Knowledge Items:** 1

### Design Guideline 1: Ensure Consistent Default Values in API Methods
**Source Discussion Time:** 00:44:38.960 - 00:45:00.080
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:44:38.960
<img src="keyframes/segment_12_guideline_1_00-44-38-960.png" alt="Key Frame at 00:44:38.960" width="600"/>

**Problem:**
Inconsistent default values in API methods can lead to unexpected behavior and confusion for developers. For instance, if a method's body shows 'unset' as a default, it may not be clear what the expected input should be, leading to errors or misconfigurations. This issue often arises in complex APIs where default values are not clearly defined or documented.

**Best Practice:**
Define and document consistent default values for all API methods to ensure predictable behavior. BEFORE: Method body shows 'unset' as default. AFTER: Method body shows a clearly defined default value, such as 'defaultValue'. This practice enhances reliability and developer trust in the API, and should be applied to all methods where defaults are relevant.

---

## Segment 13: Document Analyzer API Review
**Time Range:** 00:46:30.520 - 00:51:16.875
**Total Knowledge Items:** 1

### Design Guideline 1: Promote Key Methods to Top-Level API
**Source Discussion Time:** 00:46:30.520 - 00:51:16.875
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:46:37.062
<img src="keyframes/segment_13_guideline_1_00-46-37-062.png" alt="Key Frame at 00:46:37.062" width="600"/>

**Problem:**
In complex APIs, key methods may be buried within nested namespaces, making them less accessible and harder to discover for developers. This can lead to inefficient use of the API and increased learning curve, especially when dealing with document analysis tasks where quick access to methods like 'analyzeAsync' is crucial.

**Best Practice:**
Promote essential methods to the top-level API to enhance accessibility and usability. BEFORE: 'analyzeAsync' is nested within 'Azure AI content understanding'. AFTER: 'analyzeAsync' is directly accessible at the top level. This improves discoverability and reduces the learning curve for developers, facilitating efficient document analysis. Consider this approach for other critical methods in the API.

---

## Segment 14: Binary Content Analysis Discussion
**Time Range:** 00:51:18.720 - 00:52:44.080
**Total Knowledge Items:** 1

### Design Guideline 1: Separate Methods for Binary and Array Inputs
**Source Discussion Time:** 00:51:18.720 - 00:52:44.080
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:51:23.562
<img src="keyframes/segment_14_guideline_1_00-51-23-562.png" alt="Key Frame at 00:51:23.562" width="600"/>

**Problem:**
APIs that handle both binary and array inputs often face challenges in method naming and overloads, which can lead to confusion among developers. Having separate methods like 'analyzeBinaryAsync' and 'analyzeAsync' can make the API more intuitive, but may also cause discrepancies between library APIs and REST APIs.

**Best Practice:**
Maintain separate methods for binary and array inputs to align with REST API operations. BEFORE: Single method 'analyzeAsync' with overloads for different input types. AFTER: Separate methods 'analyzeAsync' for array inputs and 'analyzeBinaryAsync' for binary inputs. This approach ensures consistency with REST API documentation and improves method discoverability in library APIs. Consider this pattern when designing APIs that need to handle multiple input types.

---

## Segment 15: Preview Scenario and Document Navigation
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 16: Custom Analyzer Creation and Schema Configuration
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 17: Cross-API String Encoding Issue
**Time Range:** 01:09:25.600 - 01:17:08.312
**Total Knowledge Items:** 1

### Design Guideline 1: Handle String Encoding Across APIs
**Source Discussion Time:** 01:09:25.600 - 01:17:08.312
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:09:29.920
<img src="keyframes/segment_17_guideline_1_01-09-29-920.png" alt="Key Frame at 01:09:29.920" width="600"/>

**Problem:**
APIs often need to handle text strings that span different character encoding systems, such as UTF-16 code units or Unicode code points. This can lead to inconsistencies and errors when processing text across different programming languages. For example, a span indicating a range within a text string may be interpreted differently in JavaScript versus Python due to their distinct character encoding systems. This issue is problematic because it can cause incorrect text processing and data corruption, especially in multilingual applications.

**Best Practice:**
To address cross-API string encoding issues, APIs should provide a mechanism for users to specify the character encoding system they are using. This can be achieved by introducing a property like 'string encoding' that allows users to define their preferred encoding method. BEFORE: `span = get_span(text)` AFTER: `span = get_span(text, encoding='UTF-16')`. This approach ensures consistent text processing across different languages and prevents data corruption. It is particularly useful in applications that handle multilingual text or require precise text manipulation.

---

## Segment 18: String Encoding Discussion
**Time Range:** 01:23:25.180 - 01:26:26.688
**Total Knowledge Items:** 1

### Design Guideline 1: Choose Appropriate String Encoding
**Source Discussion Time:** 01:23:25.180 - 01:26:26.688
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:23:33.875
<img src="keyframes/segment_18_guideline_1_01-23-33-875.png" alt="Key Frame at 01:23:33.875" width="600"/>

**Problem:**
Choosing the wrong string encoding can lead to data corruption and misinterpretation. For instance, using 'character encoding' without specifying endianness can cause issues in data processing. Developers often struggle with selecting the right encoding for their applications, especially when dealing with cross-platform SDKs where default encodings may vary.

**Best Practice:**
Select 'string encoding' that aligns with the natural encoding of the SDK being used. For example, use 'UTF-8' for web applications and 'UTF-16' for Windows applications. This ensures data integrity and consistency across platforms. Document the chosen encoding and its rationale to aid developers in understanding the implications. Apply this pattern when developing SDKs to ensure that encoding choices are clear and appropriate for the target platform.

---

## Segment 19: API Naming Conventions and Type Specifications
**Time Range:** 01:26:34.540 - 01:28:22.125
**Total Knowledge Items:** 1

### Design Guideline 1: Align API Naming with RESTful Conventions
**Source Discussion Time:** 01:26:34.540 - 01:28:22.125
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:27:25.312
<img src="keyframes/segment_19_guideline_1_01-27-25-312.png" alt="Key Frame at 01:27:25.312" width="600"/>

**Problem:**
Inconsistent naming conventions between REST APIs and SDKs can lead to confusion and errors. For example, using 'in' in naming units can conflict with established REST API guidelines, causing discrepancies in documentation and implementation. Developers may struggle to maintain consistency across different platforms and languages.

**Best Practice:**
Adopt RESTful API naming conventions across SDKs to ensure consistency. For instance, avoid using 'in' when naming units and follow established guidelines for naming conventions. This approach reduces confusion and aligns SDKs with widely accepted standards, improving developer experience and reducing errors. Apply this pattern when designing APIs to ensure uniformity across different platforms and languages.

---

## Segment 20: API Design and Naming Conventions
**Time Range:** 01:26:28.940 - 01:34:27.562
**Total Knowledge Items:** 2

### Design Guideline 1: Use Plain Strings for Extensible Enums
**Source Discussion Time:** 01:26:28.940 - 01:26:34.140
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:26:30.938
<img src="keyframes/segment_20_guideline_1_01-26-30-938.png" alt="Key Frame at 01:26:30.938" width="600"/>

**Problem:**
Using extensible enum patterns can lead to complexity and confusion in API design. A common issue is the use of enums to represent a set of string values, which can become difficult to manage as the API evolves. This pattern often results in poor developer experience as it requires constant updates to the enum definitions and documentation, which may be overlooked. It is problematic because it can lead to type safety issues and increased maintenance overhead. This problem frequently occurs in APIs where flexibility in value representation is needed, such as configuration settings or metadata fields.

**Best Practice:**
The recommended approach is to use plain strings instead of extensible enums for fields that require flexibility in value representation. This simplifies the API design and reduces maintenance overhead. BEFORE: `enum EncodingType { UTF8, ASCII }` AFTER: `string encodingType = "UTF8";` This approach improves developer experience by allowing easy updates to allowable values without changing the API contract. It is particularly beneficial in scenarios where the set of values is expected to change over time. Alternative approaches include using a validation mechanism to ensure string values conform to expected patterns. Apply this pattern when designing fields that require extensibility and flexibility.

### Design Guideline 2: Follow REST API Naming Conventions
**Source Discussion Time:** 01:27:24.860 - 01:34:27.562
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:27:01.750
<img src="keyframes/segment_20_guideline_2_01-27-01-750.png" alt="Key Frame at 01:27:01.750" width="600"/>

**Problem:**
Inconsistent naming conventions across different APIs can lead to confusion and errors. A common issue is the use of different naming patterns for similar concepts, such as units of measurement. This inconsistency can result in poor developer experience as it requires developers to remember different conventions for different APIs. It is problematic because it can lead to misunderstandings and integration issues. This problem often occurs in APIs that are part of a larger ecosystem, where consistency is crucial for seamless integration.

**Best Practice:**
The recommended solution is to adhere to established REST API naming conventions, such as appending units to the end of field names without additional words. BEFORE: `string lengthInMeters` AFTER: `string lengthMeters` This approach improves consistency and reduces cognitive load for developers, making APIs easier to use and integrate. It is particularly beneficial in scenarios where APIs are part of a larger ecosystem, such as cloud services. Alternative approaches include documenting naming conventions clearly and providing examples. Apply this pattern when designing APIs that need to align with existing standards or conventions.

---

## Segment 21: Code Review and Comment Resolution
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 22: Resource Identifier and Nullability Discussion
**Time Range:** 01:38:50.460 - 01:39:05.100
**Total Knowledge Items:** 1

### Design Guideline 1: Utilize Specific Types for Resource Identifiers
**Source Discussion Time:** 01:38:50.460 - 01:39:05.100
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:39:01.688
<img src="keyframes/segment_22_guideline_1_01-39-01-688.png" alt="Key Frame at 01:39:01.688" width="600"/>

**Problem:**
Using generic types for resource identifiers in APIs can lead to confusion and errors. For example, a method that accepts a string as a resource ID does not provide type safety or clarity, making it difficult for developers to understand what kind of resource is being referenced. This issue is prevalent in APIs where resource identifiers are frequently used but not clearly defined.

**Best Practice:**
To enhance type safety and clarity, use specific types for resource identifiers, such as a dedicated ResourceIdentifier class. This approach provides a clear contract for what constitutes a valid resource ID, improving developer experience and reducing errors. Before: `def getResource(id: str):` After: `def getResource(id: ResourceIdentifier):`. This pattern should be applied in APIs where resource identifiers are a common element.

---

## Segment 23: API Type Representation and Naming Conventions
**Time Range:** 01:44:51.688 - 01:48:43.312
**Total Knowledge Items:** 1

### Design Guideline 1: Use Specific Types for Geometric Shapes
**Source Discussion Time:** 01:44:51.688 - 01:48:43.312
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:47:05.562
<img src="keyframes/segment_23_guideline_1_01-47-05-562.png" alt="Key Frame at 01:47:05.562" width="600"/>

**Problem:**
Using generic types like 'rectangle' to represent geometric shapes can lead to ambiguity and errors in API design. For instance, using a list of 8 values to represent a rectangle might not accurately convey the intended shape, especially if the shape is actually a polygon. This can result in poor developer experience and maintainability issues, as developers may misinterpret the data structure or struggle with type safety.

**Best Practice:**
Define specific types or classes to represent geometric shapes in APIs, such as 'Polygon' or 'Rectangle'. This approach improves clarity and type safety. For example, instead of using a list of values, define a class 'Polygon' with properties for vertices. This enhances developer experience by providing clear, understandable data structures. Consider using wrapper classes to encapsulate complex types, ensuring better maintainability and reducing errors.

---

## Segment 24: API Location and Geography Naming Discussion
**Time Range:** 01:48:45.250 - 01:50:23.000
**Total Knowledge Items:** 1

### Design Guideline 1: Flexible API Location Specification
**Source Discussion Time:** 01:48:45.250 - 01:50:23.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:48:45.250
<img src="keyframes/segment_24_guideline_1_01-48-45-250.png" alt="Key Frame at 01:48:45.250" width="600"/>

**Problem:**
APIs often require specifying the location where a service call should be executed. Using ambiguous or inconsistent naming for location parameters can lead to confusion and errors. For example, using 'region' or 'geography' interchangeably without clear guidelines can result in poor developer experience and misconfigured service calls. This issue is common in APIs dealing with global services where data locality is crucial.

**Best Practice:**
Adopt a clear and consistent naming convention for location parameters in APIs. Use terms like 'global', 'data zone', or 'resource geography' with precise definitions. BEFORE: `def analyze_call(location='region')` AFTER: `def analyze_call(location='data_zone')`. This improves clarity and ensures developers understand the implications of their choices. Consider providing default options like 'global' for flexibility. Apply this pattern in APIs where service call locality impacts performance or compliance.

---

## Segment 25: Core API Design and Release Planning
**Time Range:** 01:50:20.060 - 01:50:53.020
**Total Knowledge Items:** 1

### Design Guideline 1: Resource Integration in Core API
**Source Discussion Time:** 01:50:20.060 - 01:50:53.020
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:50:24.938
<img src="keyframes/segment_25_guideline_1_01-50-24-938.png" alt="Key Frame at 01:50:24.938" width="600"/>

**Problem:**
Integrating shared concepts into a core API can lead to expensive design costs and may not be worth the effort if the library does not justify it. For example, making a resource a core part of the API without clear benefits can result in increased complexity and maintenance overhead. This issue often arises when deciding whether to centralize common functionalities in a core library.

**Best Practice:**
Evaluate the necessity and benefits of integrating shared concepts into a core API. BEFORE: `def create_resource()` in core API without clear justification. AFTER: `def create_resource()` in a separate module if the core integration is not justified. This approach helps manage design costs and complexity. Consider the impact on library usability and maintenance before making such decisions.

---
