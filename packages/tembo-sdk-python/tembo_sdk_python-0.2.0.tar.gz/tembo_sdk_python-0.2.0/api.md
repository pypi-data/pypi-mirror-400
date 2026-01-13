# Me

Types:

```python
from tembo.types import MeRetrieveResponse
```

Methods:

- <code title="get /me">client.me.<a href="./src/tembo/resources/me.py">retrieve</a>() -> <a href="./src/tembo/types/me_retrieve_response.py">MeRetrieveResponse</a></code>

# Task

Types:

```python
from tembo.types import TaskCreateResponse, TaskListResponse, TaskSearchResponse
```

Methods:

- <code title="post /task/create">client.task.<a href="./src/tembo/resources/task.py">create</a>(\*\*<a href="src/tembo/types/task_create_params.py">params</a>) -> <a href="./src/tembo/types/task_create_response.py">TaskCreateResponse</a></code>
- <code title="get /task/list">client.task.<a href="./src/tembo/resources/task.py">list</a>(\*\*<a href="src/tembo/types/task_list_params.py">params</a>) -> <a href="./src/tembo/types/task_list_response.py">TaskListResponse</a></code>
- <code title="get /task/search">client.task.<a href="./src/tembo/resources/task.py">search</a>(\*\*<a href="src/tembo/types/task_search_params.py">params</a>) -> <a href="./src/tembo/types/task_search_response.py">TaskSearchResponse</a></code>

# Repository

Types:

```python
from tembo.types import RepositoryListResponse
```

Methods:

- <code title="get /repository/list">client.repository.<a href="./src/tembo/resources/repository.py">list</a>() -> <a href="./src/tembo/types/repository_list_response.py">RepositoryListResponse</a></code>
