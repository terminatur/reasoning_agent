# Programming Guidelines

This file defines general programming guidelines and coding standards to follow throughout the project. These rules ensure code quality, maintainability, and consistency across all development work.

## File Documentation Standards

### 1. File Header Comments
Every code file MUST include a commented paragraph at the top containing:
- **Purpose**: What this file is and its role in the system
- **Functionality**: What it semantically does and its key responsibilities  
- **Update Trigger**: When this file should be modified or updated
- **Last Modified**: Date of last significant change

**Example for Python:**
```python
"""
File: src/data/user_manager.py
Purpose: Manages user authentication and profile data operations
Functionality: Handles user login, logout, profile CRUD operations, and session management
Update Trigger: When authentication logic changes, new user fields added, or session handling modified
Last Modified: 2024-06-24
"""
```

**Example for JavaScript:**
```javascript
/**
 * File: src/components/UserCard.js
 * Purpose: Reusable user profile display component
 * Functionality: Renders user information with avatar, name, email, and action buttons
 * Update Trigger: When user data structure changes or new display requirements added
 * Last Modified: 2024-06-24
 */
```

**CRITICAL**: This header comment MUST be updated whenever the file is modified.

## Code Organization Standards

### 2. File Size Limits
- Keep all code files under **500 lines of code**
- If a file exceeds this limit, refactor into smaller, focused modules
- Comments and blank lines don't count toward the limit
- This ensures easier code navigation and AI agent analysis

### 3. Single Responsibility Principle
- Each file MUST contain only **one class** (for object-oriented languages)
- Each file should have a single, well-defined purpose
- Split large classes into smaller, focused classes in separate files
- Use composition and dependency injection for complex relationships

**Example file structure:**
```
src/
  models/
    User.py          # Only User class
    Product.py       # Only Product class
    Order.py         # Only Order class
  services/
    UserService.py   # Only UserService class
    EmailService.py  # Only EmailService class
```

## Documentation Standards

### 4. File Path References
- Always provide **relative file paths** in documentation
- Use paths relative to the project root directory
- This prevents confusion with files having identical names

**Example in documentation:**
```markdown
## User Management Components
- `src/models/User.py` - User data model
- `src/services/UserService.py` - User business logic
- `tests/models/User.py` - User model tests (different from model file)
```

**In code comments:**
```python
# See src/config/database.py for connection settings
# Related validation logic in src/utils/validators.py
```

## Type Safety Standards

### 5. Strong Typing Requirements
- **ALWAYS** use type hints for all function parameters and return types
- **ALWAYS** use type hints for variables when type is not obvious from assignment
- Use specific types rather than generic ones (e.g., `List[str]` instead of `List`)
- Import typing modules at the top of the file

**❌ Bad:**
```python
def process_user_data(data, user_id, options=None):
    if options is None:
        options = {}
    result = []
    for item in data:
        processed = transform_item(item, user_id)
        result.append(processed)
    return result
```

**✅ Good:**
```python
from typing import List, Dict, Any, Optional

def process_user_data(
    data: List[Dict[str, Any]], 
    user_id: int, 
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    if options is None:
        options = {}
    result: List[Dict[str, Any]] = []
    for item in data:
        processed: Dict[str, Any] = transform_item(item, user_id)
        result.append(processed)
    return result
```

### 6. Pydantic Model Standards
- **ALWAYS** use Pydantic for data models and entities
- Use Pydantic's built-in validation features
- Define clear field types and validation rules
- Use Pydantic's `BaseModel` for all data classes

**❌ Bad:**
```python
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
```

**✅ Good:**
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
```

**Pydantic Benefits:**
- Automatic data validation
- Type coercion and conversion
- Clear error messages
- JSON serialization/deserialization
- IDE support and autocompletion

## Security Standards

### 7. No Hardcoded Secrets
- **NEVER** hardcode API keys, passwords, tokens, or sensitive data
- Use environment variables for all secrets
- Use configuration files for non-sensitive settings
- Document required environment variables

**❌ Bad:**
```python
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"
```

**✅ Good:**
```python
import os
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

if not API_KEY:
    raise ValueError("API_KEY environment variable is required")
```

**Environment file example (.env):**
```
API_KEY=your_api_key_here
DATABASE_URL=your_database_url_here
SECRET_KEY=your_secret_key_here
```

## Implementation Checklist

Before committing any code file, verify:
- [ ] File header comment is present and accurate
- [ ] File is under 500 lines of code
- [ ] Only one class per file (if applicable)
- [ ] All functions have type hints for parameters and return types
- [ ] Variables have type hints when type is not obvious
- [ ] Data models use Pydantic BaseModel
- [ ] No hardcoded secrets or sensitive data
- [ ] File paths in comments/docs are relative to project root
- [ ] Header comment updated if file was modified

## Enforcement

These guidelines are enforced through:
1. Code review process
2. Automated linting and static analysis
3. AI agent adherence during development
4. Regular codebase audits

Violations should be addressed immediately to maintain code quality and project standards.
