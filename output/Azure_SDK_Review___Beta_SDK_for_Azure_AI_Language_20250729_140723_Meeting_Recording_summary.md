# API/SDK Design Guidelines
**Extracted from:** Azure SDK Review - [Beta SDK for Azure AI Language]-20250729_140723-Meeting Recording.mp4

> This document contains reusable API/SDK design principles and best practices extracted from technical review meetings.
> These guidelines can be used by developers and LLMs to review APIs or design better SDKs.

**Total Topics:** 26
**Total Design Guidelines:** 17

---

## Segment 1: Meeting Opening and Introductions
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 2: Meeting Opening and SDK Overview
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 3: Core SDK Design Discussion
**Time Range:** 00:08:19.938 - 00:16:35.875
**Total Knowledge Items:** 1

### Design Guideline 1: Use Operation Groups for Method Compartmentalization
**Source Discussion Time:** 00:08:19.938 - 00:16:35.875
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:08:19.938
<img src="keyframes/segment_3_guideline_1_00-08-19-938.png" alt="Key Frame at 00:08:19.938" width="600"/>

**Problem:**
In SDK design, overwhelming the base client with numerous methods can lead to poor developer experience. A common anti-pattern is having a single client with all operations, requiring repetitive parameter passing, such as 'project_name' in every method call. This can make the SDK cumbersome and difficult to navigate, especially in complex projects with multiple entities like 'deployment' and 'project'.

**Best Practice:**
Adopt operation groups to compartmentalize methods according to entities, reducing the number of operations on the base client. BEFORE: 'client.create_project(project_name, details)' repeated for each method. AFTER: 'client.project_operations.create(details)' with 'project_name' set once. This approach improves usability by organizing methods logically, reducing repetitive parameter passing, and aligning with common SDK design practices. Consider using sub-clients for scenarios requiring stateful interactions.

---

## Segment 4: Advanced SDK Design Considerations
**Time Range:** 00:16:16.500 - 00:24:46.500
**Total Knowledge Items:** 1

### Design Guideline 1: Balance Between Sub-Clients and Operation Groups
**Source Discussion Time:** 00:16:16.500 - 00:24:46.500
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:16:16.500
<img src="keyframes/segment_4_guideline_1_00-16-16-500.png" alt="Key Frame at 00:16:16.500" width="600"/>

**Problem:**
In API design, managing multiple projects can become cumbersome if the SDK requires repetitive parameter passing for each operation. This is particularly problematic when dealing with project-specific operations where the project name must be passed repeatedly, leading to inefficiency and poor developer experience. This issue is exacerbated when the SDK design does not align with common practices across different languages, such as .NET and Python.

**Best Practice:**
Consider making project-specific parameters optional at the client constructor level, allowing them to be set once and reused across operations. BEFORE: 'client.operation_group.method(project_name, details)' for each call. AFTER: 'client.method(details)' with project_name set at initialization. This approach reduces redundancy, aligns with cross-language SDK design practices, and improves usability by allowing developers to manage multiple projects efficiently without maintaining separate clients for each. Evaluate the use of operation groups versus sub-clients based on typical usage scenarios and customer needs.

---

## Segment 5: SDK Client Structure and Project Management
**Time Range:** 00:24:29.625 - 00:29:21.750
**Total Knowledge Items:** 1

### Design Guideline 1: Optional Project Name in Client Constructor
**Source Discussion Time:** 00:24:29.625 - 00:29:21.750
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:24:29.625
<img src="keyframes/segment_5_guideline_1_00-24-29-625.png" alt="Key Frame at 00:24:29.625" width="600"/>

**Problem:**
In SDK design, requiring developers to repeatedly pass project names for operations can lead to inefficiency and a cumbersome user experience. This is especially problematic when the number of projects is dynamic and not fixed, requiring developers to manage multiple clients or collections of clients. This pattern can break when settings are dynamically instantiated, leading to increased complexity in managing client instances.

**Best Practice:**
Introduce an optional project name parameter at the client constructor level, allowing it to be set once and reused across operations. BEFORE: 'client.operation_group.method(project_name, details)' for each call. AFTER: 'client.method(details)' with project_name set at initialization. This reduces redundancy and aligns with common SDK practices, improving usability by allowing developers to manage multiple projects efficiently without maintaining separate clients for each. Consider scenarios where project names are dynamic and ensure the SDK can handle such cases effectively.

---

## Segment 6: SDK Development and Language Support
**Time Range:** 00:29:23.625 - 00:32:56.500
**Total Knowledge Items:** 1

### Design Guideline 1: Prioritize Language Support for SDKs
**Source Discussion Time:** 00:29:23.625 - 00:32:56.500
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:31:45.250
<img src="keyframes/segment_6_guideline_1_00-31-45-250.png" alt="Key Frame at 00:31:45.250" width="600"/>

**Problem:**
When developing SDKs for an API, failing to prioritize language support can lead to limited adoption and integration challenges. For example, if an API is primarily used in Python environments but lacks a Python SDK, developers may face difficulties in implementation. This issue often arises when APIs are designed without considering the primary languages used by their target audience, leading to poor developer experience and reduced usability.

**Best Practice:**
To ensure broad adoption and ease of integration, prioritize SDK development for languages most relevant to your user base. For instance, if your API is widely used in Python, focus on creating a robust Python SDK first. BEFORE: API with limited language support. AFTER: API with comprehensive SDKs for Python, C#, JavaScript, and Java. This approach improves developer experience and facilitates easier integration. Consider alternative languages based on user feedback and market trends.

---

## Segment 7: Client Structure and Operation Groups
**Time Range:** 00:32:56.500 - 00:34:03.000
**Total Knowledge Items:** 1

### Design Guideline 1: Use Operation Groups for Client Structure
**Source Discussion Time:** 00:32:56.500 - 00:34:03.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:33:22.312
<img src="keyframes/segment_7_guideline_1_00-33-22-312.png" alt="Key Frame at 00:33:22.312" width="600"/>

**Problem:**
In API client design, using operation clients instead of operation groups can lead to unnecessary complexity and maintenance challenges. For example, creating multiple sub-clients for each operation can result in repetitive code and increased overhead. This issue is common when APIs are structured without considering the benefits of grouping operations, leading to poor scalability and maintainability.

**Best Practice:**
To simplify client structure and reduce maintenance overhead, use operation groups instead of operation clients. BEFORE: Multiple sub-clients for each operation. AFTER: Consolidated operation groups with minimal repetition. This approach enhances scalability and maintainability by reducing code duplication and simplifying the client interface. Consider this pattern when designing APIs to improve developer experience and streamline operations.

---

## Segment 8: Code Generation and Technical Limitations
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 9: API Parameter Consistency Discussion
**Time Range:** 00:36:24.320 - 00:36:38.720
**Total Knowledge Items:** 1

### Design Guideline 1: Ensure Consistent Parameter Usage
**Source Discussion Time:** 00:36:24.320 - 00:36:38.720
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:36:39.625
<img src="keyframes/segment_9_guideline_1_00-36-39-625.png" alt="Key Frame at 00:36:39.625" width="600"/>

**Problem:**
Inconsistent parameter usage across similar API operations can lead to confusion and errors. For example, three list operations might take the same parameters but have different expected inputs or outputs, causing developers to misunderstand the API's functionality. This issue often arises when APIs evolve without a unified design strategy, leading to fragmented and inconsistent interfaces.

**Best Practice:**
Adopt a consistent parameter usage strategy across similar API operations. For instance, ensure that list operations with similar functionality use the same parameter names and types. BEFORE: def list_resources(project_name) vs. def list_deployments(product_name). AFTER: def list_resources(name) and def list_deployments(name). This approach improves developer experience by reducing confusion and potential errors. Apply this pattern when designing or refactoring APIs to ensure clarity and consistency.

---

## Segment 10: Client Renaming and Model Naming Strategy
**Time Range:** 00:40:11.280 - 00:43:20.000
**Total Knowledge Items:** 1

### Design Guideline 1: Avoid Unnecessary Prefixes in Model Names
**Source Discussion Time:** 00:40:11.280 - 00:43:20.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:41:33.312
<img src="keyframes/segment_10_guideline_1_00-41-33-312.png" alt="Key Frame at 00:41:33.312" width="600"/>

**Problem:**
In many SDKs, model names are prefixed to ensure global uniqueness, which can lead to overly verbose and redundant naming conventions. This practice is common in languages like .NET where namespace conflicts are more prevalent. However, in Python, this can result in cumbersome code and reduced readability, as developers often import models with context-specific aliases. The problem arises when SDKs have overlapping names, causing confusion and requiring additional aliasing.

**Best Practice:**
Adopt a naming strategy that avoids unnecessary prefixes in model names, especially in languages like Python where context is provided through imports. BEFORE: 'class ConversationAuthoringResponse'. AFTER: 'class AuthoringResponse'. This approach improves readability and reduces the need for aliasing, enhancing developer experience. Consider exceptions where prefixes are necessary for clarity, such as generic HTTP terms. Apply this pattern when designing SDKs with overlapping concepts.

---

## Segment 11: Namespace and Async Naming Discussion
**Time Range:** 00:43:20.938 - 00:44:37.438
**Total Knowledge Items:** 1

### Design Guideline 1: Avoid Redundant Async Suffixes in Namespaces
**Source Discussion Time:** 00:43:20.938 - 00:44:37.438
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:43:51.938
<img src="keyframes/segment_11_guideline_1_00-43-51-938.png" alt="Key Frame at 00:43:51.938" width="600"/>

**Problem:**
In API design, adding 'async' as a suffix to class names or methods can lead to redundancy, especially when the context already indicates asynchronous behavior. This can clutter the namespace and reduce clarity. The issue is prevalent in projects where asynchronous operations are the norm, and the namespace already implies async functionality.

**Best Practice:**
Remove redundant 'async' suffixes when the namespace or context already indicates asynchronous behavior. BEFORE: 'class AsyncConversationClient'. AFTER: 'class ConversationClient'. This enhances clarity and reduces unnecessary complexity. Use namespaces like '.AIO' to imply async behavior, allowing developers to focus on functionality rather than naming conventions. Apply this pattern when async behavior is contextually clear and does not require explicit naming.

---

## Segment 12: Long-Running Operations and Status Methods
**Time Range:** 00:44:39.188 - 00:48:04.938
**Total Knowledge Items:** 1

### Design Guideline 1: Consider Exposing Status Methods for Long-Running Operations
**Source Discussion Time:** 00:44:39.188 - 00:48:04.938
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:47:57.938
<img src="keyframes/segment_12_guideline_1_00-47-57-938.png" alt="Key Frame at 00:47:57.938" width="600"/>

**Problem:**
In API design, long-running operations often require status checks to inform users of their progress. However, exposing status methods can lead to redundancy if the information is already available through other means, such as pollers. This issue arises when operations run for extended periods, making it impractical to keep pollers active. Developers may face challenges in tracking the status of multiple operations without dedicated methods.

**Best Practice:**
Expose status methods for long-running operations when pollers are impractical due to extended durations. BEFORE: Relying solely on pollers for status updates. AFTER: Providing dedicated 'get_status' methods for operations expected to run for days. This approach improves usability by allowing developers to track multiple operations efficiently. Consider alternative methods like event-driven updates for real-time status tracking. Apply this pattern when operations exceed typical poller durations and require independent status checks.

---

## Segment 13: Naming Conventions and Documentation
**Time Range:** 00:48:04.938 - 00:55:42.438
**Total Knowledge Items:** 1

### Design Guideline 1: Refine Naming Conventions for Clarity
**Source Discussion Time:** 00:48:04.938 - 00:55:42.438
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:48:04.938
<img src="keyframes/segment_13_guideline_1_00-48-04-938.png" alt="Key Frame at 00:48:04.938" width="600"/>

**Problem:**
API methods with complex or unclear names can confuse developers and hinder usability. Names like 'get_deployment_delete_from_resource_status' are difficult to understand and may not accurately convey the method's purpose. This issue is common when names are derived from specifications without considering developer experience.

**Best Practice:**
Refine naming conventions to enhance clarity and usability. BEFORE: Using complex names derived from specifications. AFTER: Simplifying names to clearly reflect the method's purpose, such as 'get_deployment_deletion_status'. This improves developer experience by making APIs more intuitive. Consider aligning names with common language patterns used by developers. Apply this pattern when naming methods to ensure they are easily understood and accurately represent their functionality.

---

## Segment 14: Documentation Practices and Method Clarity
**Time Range:** 00:55:42.438 - 00:57:58.750
**Total Knowledge Items:** 1

### Design Guideline 1: Enhance Documentation for Method Clarity
**Source Discussion Time:** 00:55:42.438 - 00:57:58.750
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:56:23.188
<img src="keyframes/segment_14_guideline_1_00-56-23-188.png" alt="Key Frame at 00:56:23.188" width="600"/>

**Problem:**
Lack of clear documentation for API methods can lead to confusion and misuse by developers. Without detailed explanations of what each method does and the parameters it expects, developers may struggle to implement the API correctly. This issue is prevalent when documentation is not auto-generated or standardized across platforms.

**Best Practice:**
Implement comprehensive documentation practices for API methods. BEFORE: Minimal or unclear documentation leading to developer confusion. AFTER: Detailed documentation explaining each method's purpose, expected parameters, and usage examples. This enhances developer experience by providing clear guidance and reducing implementation errors. Consider using auto-generation tools to ensure consistency and completeness across all methods. Apply this pattern to improve API usability and developer satisfaction.

---

## Segment 15: Code Generation and Client Constructor Discussion
**Time Range:** 00:58:05.500 - 00:58:29.125
**Total Knowledge Items:** 1

### Design Guideline 1: Utilize Code Generation for Path Parameters
**Source Discussion Time:** 00:58:05.500 - 00:58:29.125
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 00:58:20.688
<img src="keyframes/segment_15_guideline_1_00-58-20-688.png" alt="Key Frame at 00:58:20.688" width="600"/>

**Problem:**
Manually adding path parameters to client constructors can lead to errors and inconsistencies. Developers often need to patch code manually, which is time-consuming and error-prone. This issue arises when APIs require dynamic path parameters that are not supported by default in client constructors, leading to poor developer experience and maintainability challenges.

**Best Practice:**
Leverage code generation tools to automatically add path parameters to client constructors. This approach reduces manual patching and ensures consistency across API implementations. BEFORE: `def __init__(self, project_name): self.project_name = project_name` AFTER: `def __init__(self, path_param): self.path_param = path_param`. This improves developer experience by automating repetitive tasks and reducing errors. Apply this pattern when dealing with dynamic path parameters in APIs.

---

## Segment 16: Exported Model and Container Offering Discussion
**Time Range:** 01:00:44.438 - 01:02:55.312
**Total Knowledge Items:** 1

### Design Guideline 1: Enable Model Export for Containerized Services
**Source Discussion Time:** 01:00:44.438 - 01:02:55.312
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:01:00.250
<img src="keyframes/segment_16_guideline_1_01-01-00-250.png" alt="Key Frame at 01:01:00.250" width="600"/>

**Problem:**
APIs that offer containerized services often face challenges in model retrieval and deployment. Without a clear mechanism to export models, customers running containers independently may struggle to access and utilize trained models effectively. This can lead to inefficiencies and barriers in deploying custom models within container environments.

**Best Practice:**
Implement an exported model feature that allows customers to retrieve trained models from storage accounts for use in containerized services. BEFORE: Customers manually download models from storage. AFTER: An API endpoint provides automated model export functionality. This enhances the deployment process by streamlining model access and integration into containerized environments. Apply this pattern when offering containerized services that require model deployment.

---

## Segment 17: Model Export Status and Documentation
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 18: Polymorphic Model Attributes Discussion
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 19: Model Naming Clash and Polymorphism
**Time Range:** 01:05:38.290 - 01:05:56.450
**Total Knowledge Items:** 1

### Design Guideline 1: Avoid Naming Clashes in Models
**Source Discussion Time:** 01:05:38.290 - 01:05:56.450
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:05:44.562
<img src="keyframes/segment_19_guideline_1_01-05-44-562.png" alt="Key Frame at 01:05:44.562" width="600"/>

**Problem:**
Naming clashes in models can occur when a property name conflicts with a method name, leading to confusion and potential errors in code generation or API usage. This is problematic because it can cause unexpected behavior and make the API difficult to understand and use. Common scenarios include models that act as mappings or collections, where method names like 'values' may conflict with property names.

**Best Practice:**
To avoid naming clashes, ensure that property names and method names are distinct and do not overlap. Use clear and descriptive names for properties and methods, and consider adding suffixes or prefixes to differentiate them. BEFORE: `class Model: def values(): pass property values`. AFTER: `class Model: def get_values(): pass property values_property`. This approach improves code clarity and prevents errors in API usage. Apply this pattern in scenarios where models have dual roles or complex behaviors.

---

## Segment 20: Naming Conventions in SDKs
**Time Range:** 01:06:38.460 - 01:06:58.700
**Total Knowledge Items:** 1

### Design Guideline 1: Consistent Naming Conventions Across SDKs
**Source Discussion Time:** 01:06:38.460 - 01:06:58.700
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:06:54.438
<img src="keyframes/segment_20_guideline_1_01-06-54-438.png" alt="Key Frame at 01:06:54.438" width="600"/>

**Problem:**
Inconsistent naming conventions across SDKs can lead to confusion and errors. For example, using 'details' as a suffix for output models in one SDK but not in another can make it difficult for developers to understand and predict naming patterns. This inconsistency can occur when different teams work on separate SDKs without a unified naming strategy.

**Best Practice:**
Adopt a consistent naming convention across all SDKs to improve developer experience and reduce errors. For instance, use 'details' as a suffix for output models consistently across all SDKs. BEFORE: 'class UserOutput' in SDK A, 'class UserDetails' in SDK B. AFTER: 'class UserDetails' in both SDKs. This approach enhances predictability and reduces cognitive load for developers working with multiple SDKs.

---

## Segment 21: API Usage Statistics and Namespace Conclusion
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 22: API Evolution and Method Unification
**Time Range:** 01:16:09.125 - 01:17:43.000
**Total Knowledge Items:** 1

### Design Guideline 1: Unify API Endpoints for Task Flexibility
**Source Discussion Time:** 01:16:09.125 - 01:17:43.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:16:31.625
<img src="keyframes/segment_22_guideline_1_01-16-31-625.png" alt="Key Frame at 01:16:31.625" width="600"/>

**Problem:**
APIs often start with separate endpoints for each task, such as sentiment analysis or entity recognition, leading to fragmented code and increased complexity. This approach requires developers to manage multiple endpoints, which can be cumbersome and error-prone. It is common in scenarios where APIs evolve over time without a unified strategy.

**Best Practice:**
Adopt a unified endpoint approach where a single method can handle multiple tasks, such as sentiment analysis, entity recognition, and PII processing. BEFORE: `def analyze_sentiment(data):` and `def recognize_entities(data):`. AFTER: `def analyze_text(data, tasks=['sentiment', 'entities']):`. This reduces complexity and improves developer experience by allowing batch processing and task flexibility. Consider alternative approaches like modular task plugins if applicable.

---

## Segment 23: AI Language Package Review
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 24: Package Naming and Versioning Strategy
**Time Range:** 01:20:01.875 - 01:21:02.000
**Total Knowledge Items:** 1

### Design Guideline 1: Versioning Strategy for Package Updates
**Source Discussion Time:** 01:20:01.875 - 01:21:02.000
**Category:** API_DESIGN_GUIDELINE
**Reference Frame:** 01:20:01.875
<img src="keyframes/segment_24_guideline_1_01-20-01-875.png" alt="Key Frame at 01:20:01.875" width="600"/>

**Problem:**
When updating an API or SDK, developers often face the challenge of whether to release a new package or update the existing one with a major version bump. Releasing a new package can lead to fragmentation and loss of existing user base, as users may hesitate to switch to a new library. This is problematic because it disrupts continuity and can lead to decreased adoption of the new version.

**Best Practice:**
The recommended approach is to update the existing package with a major version bump rather than releasing a new package. This strategy maintains continuity and encourages users to upgrade, as the mental hurdle is lower compared to adopting a new library. Before: `package_v1` and `package_v2` as separate entities. After: `package` with version `1.x` and `2.x`. This approach keeps the package popular and retains its user base.

---

## Segment 25: Hero Scenarios and SDK Operations
**Time Range:** - - -
**Total Knowledge Items:** 0

---

## Segment 26: Meeting Conclusion and Next Steps
**Time Range:** - - -
**Total Knowledge Items:** 0

---
