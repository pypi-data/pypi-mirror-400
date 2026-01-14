# Stateful Jobs Guide

Stateful jobs allow you to persist data across multiple job executions by sharing a persistent workspace.

## How It Works

When you create a stateful job:
1. A persistent ext4 disk image is created on the agent
2. The disk is mounted at `/workspace` inside the VM
3. Any data written to `/workspace` persists after the job completes
4. Subsequent jobs with the same `workspace_id` will mount the same disk

## Basic Usage

### Option 1: Auto-generate workspace ID (recommended)

```python
from magpie import Magpie

client = Magpie(api_key="your-key", base_url="http://your-server")

# Job 1: Create workspace (workspace_id will be the request_id)
result1 = client.jobs.run_and_wait(
    name="Initialize Workspace",
    script="echo 'data' > /workspace/file.txt",
    stateful=True,
    workspace_size_gb=5  # Optional, defaults to 10GB
)

workspace_id = result1.request_id  # Use this for subsequent jobs

# Job 2: Reuse the same workspace
result2 = client.jobs.run_and_wait(
    name="Read Workspace",
    script="cat /workspace/file.txt",  # Will show 'data'
    stateful=True,
    workspace_id=workspace_id  # Reuse same workspace
)
```

### Option 2: Specify custom workspace ID

```python
# Job 1: Create with custom ID
result1 = client.jobs.run_and_wait(
    name="Init",
    script="echo 'hello' > /workspace/greeting.txt",
    stateful=True,
    workspace_id="my-project-workspace",  # Custom ID
    workspace_size_gb=10
)

# Job 2: Reuse by custom ID
result2 = client.jobs.run_and_wait(
    name="Greet",
    script="cat /workspace/greeting.txt",
    stateful=True,
    workspace_id="my-project-workspace"  # Same custom ID
)
```

## Use Cases

### 1. Iterative Data Processing

```python
# Step 1: Download data
client.jobs.run_and_wait(
    name="Download",
    script="curl https://example.com/data.csv > /workspace/data.csv",
    stateful=True,
    workspace_id="data-pipeline"
)

# Step 2: Process data
client.jobs.run_and_wait(
    name="Process",
    script="python process.py /workspace/data.csv > /workspace/results.csv",
    stateful=True,
    workspace_id="data-pipeline"
)

# Step 3: Upload results
client.jobs.run_and_wait(
    name="Upload",
    script="curl -X POST -F file=@/workspace/results.csv https://api.example.com/upload",
    stateful=True,
    workspace_id="data-pipeline"
)
```

### 2. Counter/State Machine

```python
workspace_id = "counter-demo"

for i in range(5):
    result = client.jobs.run_and_wait(
        name=f"Increment {i+1}",
        script="""
        # Read current counter
        if [ -f /workspace/counter ]; then
            COUNT=$(cat /workspace/counter)
        else
            COUNT=0
        fi

        # Increment
        COUNT=$((COUNT + 1))
        echo $COUNT > /workspace/counter
        echo "Counter is now: $COUNT"
        """,
        stateful=True,
        workspace_id=workspace_id
    )
    print(f"Run {i+1} completed")
```

### 3. Build Cache

```python
# First build - slow
client.jobs.run_and_wait(
    name="Initial Build",
    script="""
    cd /workspace
    git clone https://github.com/user/repo.git
    cd repo
    npm install
    npm run build
    """,
    stateful=True,
    workspace_id="build-cache",
    workspace_size_gb=20
)

# Subsequent builds - fast (node_modules cached)
client.jobs.run_and_wait(
    name="Rebuild",
    script="""
    cd /workspace/repo
    git pull
    npm run build
    """,
    stateful=True,
    workspace_id="build-cache"
)
```

## Important Notes

1. **Workspace Size**: Set `workspace_size_gb` on the **first job** that creates the workspace. Subsequent jobs inherit this size.

2. **Workspace ID**:
   - If not specified, defaults to the job's `request_id`
   - Can be any string (lowercase letters, numbers, hyphens)
   - Same `workspace_id` = same disk

3. **Data Location**: Always write to `/workspace/` - other directories are ephemeral

4. **Workspace Lifecycle**: Workspaces persist until explicitly deleted (future feature)

5. **Concurrency**: Multiple jobs with the same workspace_id will queue - they won't run simultaneously

## API Parameters

```python
client.jobs.run_and_wait(
    name="Job Name",
    script="your script",
    stateful=True,              # Required for stateful jobs
    workspace_id="optional-id",  # Optional, defaults to request_id
    workspace_size_gb=10,        # Optional, defaults to 10GB
)
```

## Troubleshooting

### Data not persisting?
- Verify `stateful=True` is set
- Check that `workspace_id` is the same across jobs
- Ensure data is written to `/workspace/` not `/tmp/`

### Workspace not found?
- First job creates the workspace
- Subsequent jobs must use exact same `workspace_id`

### Out of space?
- Increase `workspace_size_gb` (must recreate workspace)
- Clean up old files in `/workspace/`
