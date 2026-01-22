# API/SDK Design Guidelines
**Extracted from:** Azure SDK Review - [Beta SDK for Azure AI Content Understanding]-20250820_140608-Meeting Recording.mp4

> This document contains reusable API/SDK design principles and best practices extracted from technical review meetings.
> These guidelines can be used by developers and LLMs to review APIs or design better SDKs.

**Total Topics:** 22
**Total Design Guidelines:** 18

---

## Segment 1: Meeting Opening and Introductions
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 2: Meeting Opening and Introductions
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 3: Content Understanding Python SDK Overview
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 4: Content Understanding Python SDK Hero Scenarios
**Time Range:** 00:16:33.680 - 00:18:13.120
**Total Knowledge Items:** 4

### Design Guideline 1: Allow Direct Byte Input for Local File Analysis
**Source Discussion Time:** 00:16:33.680 - 00:17:03.440
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:24:39.750
<img src="keyframes/segment_4_guideline_1_00-24-39-750.png" alt="Key Frame at 00:24:39.750" width="600"/>

**Problem:**
APIs often require users to provide data via URLs, which can be limiting when the data is already available locally. This pattern forces developers to upload files to a server or convert them to URLs, which can be inefficient and cumbersome. It also introduces unnecessary network overhead and potential security concerns when dealing with sensitive data. This problem is common in scenarios where users need to analyze local files quickly without additional steps.

**Best Practice:**
APIs should allow direct byte input for local file analysis, enabling users to pass data as bytes directly. This approach eliminates the need for URL conversion and reduces network overhead. BEFORE: def analyze(url: str): # Requires URL AFTER: def analyze(data: bytes): # Accepts byte input directly. This pattern improves efficiency and security by allowing local file analysis without uploading data. It should be applied when users frequently work with local files.

### Design Guideline 2: Differentiate API Endpoints for URL and Binary Data
**Source Discussion Time:** 00:17:03.760 - 00:17:30.960
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:24:39.750
<img src="keyframes/segment_4_guideline_2_00-24-39-750.png" alt="Key Frame at 00:24:39.750" width="600"/>

**Problem:**
APIs that handle both URL and binary data often use the same endpoint, leading to confusion and potential errors. Developers may inadvertently pass the wrong type of data, resulting in failed requests or incorrect processing. This issue is prevalent in APIs that support multiple data formats but do not clearly differentiate between them.

**Best Practice:**
APIs should differentiate endpoints for URL and binary data, ensuring clarity and reducing errors. BEFORE: def analyze(data): # Accepts both URL and binary AFTER: def analyze_url(url: str): # Separate endpoint for URL def analyze_binary(data: bytes): # Separate endpoint for binary data. This approach improves clarity and reduces the risk of errors by clearly defining the expected data type for each endpoint. It should be applied when APIs support multiple data formats.

### Design Guideline 3: Use Type Detection for Input Parameters
**Source Discussion Time:** 00:17:45.360 - 00:18:04.520
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:24:39.750
<img src="keyframes/segment_4_guideline_3_00-24-39-750.png" alt="Key Frame at 00:24:39.750" width="600"/>

**Problem:**
APIs that rely on type detection for input parameters can become difficult to maintain. This pattern often leads to complex parsing logic to differentiate between similar types, such as strings representing URLs versus content. It can result in maintenance challenges and errors when new types are introduced or when users provide unexpected input formats.

**Best Practice:**
APIs should avoid relying solely on type detection for input parameters. Instead, use explicit keyword arguments to define expected input types. BEFORE: def analyze(input): # Type detection AFTER: def analyze(url: str = None, data: bytes = None): # Explicit keyword arguments. This approach simplifies maintenance and reduces errors by clearly defining input types. It should be applied when APIs handle multiple input formats.

### Design Guideline 4: Add Overloads for Mutually Exclusive Parameters
**Source Discussion Time:** 00:18:04.560 - 00:18:13.120
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:24:39.750
<img src="keyframes/segment_4_guideline_4_00-24-39-750.png" alt="Key Frame at 00:24:39.750" width="600"/>

**Problem:**
APIs with mutually exclusive parameters often lack clear guidance on which parameters can be used together. This can lead to confusion and errors when developers attempt to use incompatible parameters simultaneously. The problem is common in APIs that support multiple input types but do not enforce exclusivity.

**Best Practice:**
APIs should add overloads for mutually exclusive parameters, providing clear guidance on compatible parameter combinations. BEFORE: def analyze(url: str, data: bytes): # No exclusivity AFTER: def analyze(url: str): # Overload for URL def analyze(data: bytes): # Overload for binary data. This approach improves clarity and reduces errors by enforcing exclusivity. It should be applied when APIs support multiple input types.

---

## Segment 5: Content Understanding Python SDK Discussion
**Time Range:** 00:41:10.040 - 00:42:15.438
**Total Knowledge Items:** 1

### Design Guideline 1: Runtime Type Decision in Python SDK
**Source Discussion Time:** 00:41:10.040 - 00:42:15.438
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:41:58.562
<img src="keyframes/segment_5_guideline_1_00-41-58-562.png" alt="Key Frame at 00:41:58.562" width="600"/>

**Problem:**
The Python SDK currently faces challenges with type hinting due to runtime type decisions. This can lead to confusion for developers who expect compile-time type safety and clarity. The problem arises when types are determined at runtime, making it difficult to provide accurate type hints and leading to potential errors or misunderstandings in code usage. This issue is common in dynamic languages like Python where type information is often inferred rather than explicitly declared.

**Best Practice:**
To address the issue of runtime type decisions, consider implementing a more robust type hinting system that can accommodate dynamic type changes. This could involve using Python's typing module to provide optional type hints that reflect possible runtime types. BEFORE: `def get_value() -> Any`. AFTER: `def get_value() -> Optional[Union[str, int]]`. This approach helps developers understand the potential types they might encounter, improving code readability and reducing errors. Additionally, consider documenting common scenarios where type changes occur to guide developers in handling these cases effectively. Apply this pattern in SDKs where dynamic typing is prevalent.

---

## Segment 6: Custom Analyzer Creation and Configuration
**Time Range:** 00:43:13.312 - 00:46:40.000
**Total Knowledge Items:** 1

### Design Guideline 1: Define and Persist Custom Analyzers
**Source Discussion Time:** 00:43:13.312 - 00:46:40.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:45:06.625
<img src="keyframes/segment_6_guideline_1_00-45-06-625.png" alt="Key Frame at 00:45:06.625" width="600"/>

**Problem:**
Creating custom analyzers without a clear definition and persistence strategy can lead to inconsistent analysis results and resource management issues. Developers often create analyzers on-the-fly without specifying a base analyzer or configuration, resulting in analyzers that do not persist or are difficult to manage. This can occur in scenarios where multiple modalities (audio, video, document) are analyzed without a structured approach, leading to poor developer experience and maintainability challenges.

**Best Practice:**
To ensure consistent and manageable custom analyzers, define a clear base analyzer and configuration before creation. Use a structured approach to specify the base analyzer ID, configuration, and schema. For example, before: `analyzer = CustomAnalyzer()`, after: `analyzer = CustomAnalyzer(base_analyzer='audioAnalyzer', config=ContentAnalyzerConfig(enable_layout=True))`. This approach ensures analyzers are persistent and manageable, improving developer experience and resource management. Apply this pattern when dealing with multi-modality content analysis.

---

## Segment 7: Patch Operations for Analyzer Updates
**Time Range:** 00:46:41.812 - 00:48:15.188
**Total Knowledge Items:** 1

### Design Guideline 1: Implement Patch Operations for Analyzer Updates
**Source Discussion Time:** 00:46:41.812 - 00:48:15.188
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:47:01.750
<img src="keyframes/segment_7_guideline_1_00-47-01-750.png" alt="Key Frame at 00:47:01.750" width="600"/>

**Problem:**
Without patch operations, updating analyzers can be cumbersome and error-prone, requiring full redefinitions even for minor changes. This leads to inefficiencies and potential inconsistencies in analyzer configurations. Developers often face challenges when they need to update descriptions or tags without altering the entire analyzer setup, especially in dynamic environments where frequent updates are necessary.

**Best Practice:**
Utilize patch operations to update specific aspects of analyzers, such as descriptions and tags, without redefining the entire analyzer. This approach allows for efficient and targeted updates, improving maintainability and reducing errors. For example, before: `analyzer = CustomAnalyzer(description='old', tags=['tag1'])`, after: `analyzer.update(description='new', tags=['tag2'])`. This pattern enhances flexibility and supports dynamic updates, making it ideal for environments with frequent configuration changes.

---

## Segment 8: Content Understanding and Document Analysis in Python SDK
**Time Range:** 00:49:11.375 - 00:50:48.375
**Total Knowledge Items:** 1

### Design Guideline 1: Handle Document Content and Table Information
**Source Discussion Time:** 00:49:11.375 - 00:50:48.375
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:50:10.312
<img src="keyframes/segment_8_guideline_1_00-50-10-312.png" alt="Key Frame at 00:50:10.312" width="600"/>

**Problem:**
When dealing with document content in APIs, developers often face challenges in accessing detailed information such as table layouts, page dimensions, and content specifics. This can lead to incomplete data processing and hinder the ability to perform detailed analyses. Common scenarios include processing PDFs or images where dimensions and table structures are crucial for accurate data extraction.

**Best Practice:**
Implement methods to access document-specific properties such as width, height, and table layouts. For example, use `document.pages` to iterate over pages and `document.tables` to access table data. Before: `document = analyze(content)`, after: `for page in document.pages: print(page.width, page.height)`. This approach ensures comprehensive data extraction and supports detailed content analysis, improving the accuracy and utility of document processing APIs.

---

## Segment 9: Handling Null and Empty Arrays in Python SDK
**Time Range:** 00:50:48.375 - 00:53:02.760
**Total Knowledge Items:** 1

### Design Guideline 1: Differentiate Null and Empty Arrays
**Source Discussion Time:** 00:50:48.375 - 00:53:02.760
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:51:00.188
<img src="keyframes/segment_9_guideline_1_00-51-00-188.png" alt="Key Frame at 00:51:00.188" width="600"/>

**Problem:**
In API design, handling null and empty arrays can be problematic, especially when serializing data between different languages like JSON and Python. Developers often struggle with whether to return a null or an empty array, which can lead to ambiguity and misinterpretation of data. This issue is common in scenarios where APIs need to convey the absence of data versus an empty dataset.

**Best Practice:**
Clearly differentiate between null and empty arrays in API responses. For example, return `None` when no data is available and an empty array `[]` when the data is empty but the operation was performed. Before: `return []`, after: `return None if not performed else []`. This approach reduces ambiguity and improves clarity in API responses, ensuring better data interpretation and handling.

---

## Segment 10: Operation ID and Long-Running Operations in Python SDK
**Time Range:** 00:53:02.760 - 00:58:51.438
**Total Knowledge Items:** 1

### Design Guideline 1: Manage Long-Running Operations with Operation ID
**Source Discussion Time:** 00:53:02.760 - 00:58:51.438
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:56:00.375
<img src="keyframes/segment_10_guideline_1_00-56-00-375.png" alt="Key Frame at 00:56:00.375" width="600"/>

**Problem:**
Managing long-running operations in APIs can be challenging, especially when tracking the status and results of these operations. Developers often face difficulties in retrieving operation IDs and using them to check operation status or retrieve results. This can lead to inefficient workflows and increased complexity in API usage, particularly in scenarios involving document analysis or video processing.

**Best Practice:**
Utilize operation IDs to manage long-running operations effectively. Implement methods to retrieve operation status and results using these IDs. Before: `result = analyze(content)`, after: `operation_id = begin_analyze(content); status = get_operation_status(operation_id); result = get_result(operation_id)`. This approach streamlines the process of handling long-running operations, improving efficiency and reducing complexity in API workflows.

---

## Segment 11: Content Understanding and Classifier Scenarios in Python SDK
**Time Range:** 00:58:51.438 - 00:59:45.125
**Total Knowledge Items:** 1

### Design Guideline 1: Designing Effective Classifier Scenarios
**Source Discussion Time:** 00:58:51.438 - 00:59:45.125
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:59:01.250
<img src="keyframes/segment_11_guideline_1_00-59-01-250.png" alt="Key Frame at 00:59:01.250" width="600"/>

**Problem:**
Creating effective classifier scenarios in APIs can be complex, especially when dealing with diverse data types and classification needs. Developers often struggle with setting up classifiers that accurately categorize data, leading to potential misclassification and inefficiencies in data processing workflows.

**Best Practice:**
Implement robust classifier scenarios by defining clear classification categories and schemas. Before: `classifier = create_classifier(data)`, after: `classifier_schema = define_schema(categories); classifier = create_classifier(data, schema)`. This approach ensures accurate data categorization, improving the reliability and efficiency of data processing workflows. Consider using predefined schemas and categories to streamline the classifier setup process.

---

## Segment 12: Face Scenarios and API Design
**Time Range:** 00:59:46.812 - 01:01:19.640
**Total Knowledge Items:** 1

### Design Guideline 1: Flexible Input Handling for Face Comparison APIs
**Source Discussion Time:** 00:59:46.812 - 01:01:19.640
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:00:02.000
<img src="keyframes/segment_12_guideline_1_01-00-02-000.png" alt="Key Frame at 01:00:02.000" width="600"/>

**Problem:**
Face comparison APIs often require specific input formats, such as URLs or byte arrays, which can be cumbersome for developers. This rigidity can lead to confusion and errors, especially when dealing with different data sources like face IDs or strings. The problem is exacerbated when APIs do not clearly distinguish between these input types, leading to potential misinterpretation and incorrect results.

**Best Practice:**
Design face comparison APIs to accept flexible input types, such as URLs, byte arrays, or face IDs, with clear documentation on how each type should be used. BEFORE: `compare_faces(url1, url2)` (limited to URLs). AFTER: `compare_faces(source1, source2)` where `source` can be URL, bytes, or ID. This approach reduces errors and improves usability by accommodating various data sources. Consider implementing input validation to ensure correct data types are used.

---

## Segment 13: API View and Content Field Discussion
**Time Range:** 01:01:21.320 - 01:02:47.250
**Total Knowledge Items:** 1

### Design Guideline 1: Avoid Ambiguous String-Based Parameters
**Source Discussion Time:** 01:01:21.320 - 01:02:47.250
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:02:06.750
<img src="keyframes/segment_13_guideline_1_01-02-06-750.png" alt="Key Frame at 01:02:06.750" width="600"/>

**Problem:**
APIs that use string-based parameters for critical operations can lead to ambiguity and errors. Developers may misinterpret the expected format or content of these strings, especially when dealing with complex data types or operations. This can result in incorrect API usage and unexpected behavior, particularly in scenarios where precise data handling is crucial.

**Best Practice:**
Use strongly typed parameters instead of strings for critical API operations. BEFORE: `def process_data(data: str)` (ambiguous string parameter). AFTER: `def process_data(data: DataType)` where `DataType` is a well-defined class or structure. This approach enhances type safety, reduces errors, and improves code readability. Consider providing helper methods to convert between types if necessary, and document the expected data format clearly.

---

## Segment 14: Model Patching and JSON Serialization Discussion
**Time Range:** 01:02:48.938 - 01:04:14.875
**Total Knowledge Items:** 1

### Design Guideline 1: Handle JSON Serialization Carefully in Model Patching
**Source Discussion Time:** 01:02:48.938 - 01:04:14.875
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:03:10.875
<img src="keyframes/segment_14_guideline_1_01-03-10-875.png" alt="Key Frame at 01:03:10.875" width="600"/>

**Problem:**
Patching models that act as dictionaries for JSON payloads can lead to unexpected side effects. When models are manipulated, it can interfere with the internal base class responsible for JSON serialization and deserialization, causing issues in data representation and transmission. This is particularly problematic when models are used to represent complex data structures that need precise serialization.

**Best Practice:**
Ensure that any model patching is done with a clear understanding of the underlying JSON serialization mechanisms. BEFORE: Directly modifying model attributes without considering serialization impact. AFTER: Implementing controlled methods for model updates that respect serialization rules. This approach prevents unintended side effects and maintains data integrity during serialization and deserialization. Consider documenting serialization behavior and providing utility functions for safe model manipulation.

---

## Segment 15: TypeSpec Design and Helper Methods
**Time Range:** 01:04:14.875 - 01:07:06.312
**Total Knowledge Items:** 1

### Design Guideline 1: Preserve Type Information with Helper Methods
**Source Discussion Time:** 01:04:14.875 - 01:07:06.312
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:06:37.375
<img src="keyframes/segment_15_guideline_1_01-06-37-375.png" alt="Key Frame at 01:06:37.375" width="600"/>

**Problem:**
In TypeSpec, scalar types can have helper methods for initialization and conversion, which are lost when emitted into Python as simple strings. This loss of type information defeats the purpose of TypeSpec's design, which aims to provide robust type handling and conversion capabilities. The problem arises when complex type systems are simplified, leading to reduced functionality and flexibility in type management.

**Best Practice:**
Maintain type information by utilizing helper methods in TypeSpec. BEFORE: Emitting scalar types as simple strings in Python, losing type-specific methods. AFTER: Preserving type-specific methods by implementing helper functions that maintain type integrity during conversion. This approach enhances type safety and flexibility, allowing for more robust type management. Consider alternative methods for type preservation if direct implementation is not feasible.

---

## Segment 16: API Design Challenges and Solutions
**Time Range:** 01:07:06.312 - 01:13:41.562
**Total Knowledge Items:** 1

### Design Guideline 1: Handling Type Discrepancies in Code Generation
**Source Discussion Time:** 01:07:06.312 - 01:13:41.562
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:07:09.000
<img src="keyframes/segment_16_guideline_1_01-07-09-000.png" alt="Key Frame at 01:07:09.000" width="600"/>

**Problem:**
When generating code from TypeSpec, discrepancies can occur, such as properties being emitted as simple strings instead of using the intended type patterns like extensible enums or unions. This inconsistency can lead to confusion for developers and reduce the effectiveness of the API design, as it may not accurately represent the intended type system and functionality.

**Best Practice:**
To address type discrepancies in code generation, ensure that the code generator accurately maps TypeSpec definitions to the target language's type system. BEFORE: Emitting properties as simple strings, losing intended type patterns. AFTER: Implementing checks and mappings in the code generator to preserve type patterns like extensible enums and unions. This approach improves consistency and developer understanding, ensuring the API design is accurately represented. Consider using language-specific features to enhance type handling where applicable.

---

## Segment 17: Type System and Schema Discussion
**Time Range:** 01:13:43.188 - 01:15:54.312
**Total Knowledge Items:** 1

### Design Guideline 1: Preserve Type Information with Helper Methods
**Source Discussion Time:** 01:13:43.188 - 01:15:54.312
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:14:02.688
<img src="keyframes/segment_17_guideline_1_01-14-02-688.png" alt="Key Frame at 01:14:02.688" width="600"/>

**Problem:**
In API design, relying solely on basic types like strings for complex data structures can lead to loss of type information and increased risk of errors. For instance, using 'def process_data(data: str)' for JSON or XML data parsing can obscure the expected format and lead to runtime errors. This pattern is problematic as it reduces clarity and type safety, making it difficult for developers to understand and correctly implement the API.

**Best Practice:**
Adopt helper methods or dedicated classes to preserve type information and improve clarity. For example, instead of 'def process_data(data: str)', use 'def process_data(data: JsonData)'. This approach enhances type safety and developer experience by clearly defining expected input types. Consider using factory methods or static methods for parsing strings into these types, ensuring consistent and reliable input handling across the SDK. This pattern should be applied when dealing with complex data structures to improve maintainability and reduce errors.

---

## Segment 18: API Issue Navigation and Review
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 19: RESTful API and Code Generation
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 20: API Design Brainstorming and Beta 2 Planning
**Time Range:** 01:25:37.980 - 01:26:54.688
**Total Knowledge Items:** 1

### Design Guideline 1: Brainstorming API Enhancements
**Source Discussion Time:** 01:25:37.980 - 01:26:54.688
**Category:** MEETING_CONTEXT
**Reference Frame:** 01:25:38.125
<img src="keyframes/segment_20_guideline_1_01-25-38-125.png" alt="Key Frame at 01:25:38.125" width="600"/>

**Problem:**
The current API design may not fully leverage IDE capabilities for code generation and analysis. This can lead to inefficiencies in how developers interact with the API, potentially requiring more manual coding and less automation. The problem is that without smart integration with IDEs, developers might miss out on features that could simplify their workflow and improve productivity.

**Best Practice:**
Set up a brainstorming session to explore how IDE integration can be enhanced. Consider using IDE plugins or extensions that can automatically generate code or analyze API usage patterns. This approach can improve developer experience by reducing manual coding efforts and increasing automation. It is recommended to keep the current design for Beta 2 and explore these enhancements for future releases.

---

## Segment 21: API Conversations and Follow-up Actions
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 22: Meeting Conclusion and Process Discussion
**Time Range:** - - -
**Total Knowledge Items:** 0

---
