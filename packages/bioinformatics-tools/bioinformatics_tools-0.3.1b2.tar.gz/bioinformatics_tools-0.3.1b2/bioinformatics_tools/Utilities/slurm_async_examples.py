"""
Examples of different async patterns for SLURM job monitoring
"""
import asyncio
import sys
from pathlib import Path

from bioinformatics_tools.utilities.ssh_slurm_async import AsyncSLURMJob

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))



# ============================================================================
# Example 1: Simple submit, monitor, then process results
# ============================================================================

async def example_simple():
    """Submit job, wait for completion, then process results"""
    slurm = AsyncSLURMJob()

    script = "echo 'Analysis complete' > ~/result.txt"
    job_id = slurm.submit_job(script, cpus=2, mem='2G', time='00:10:00')

    # Monitor until complete
    await slurm.monitor_job(job_id, poll_interval=5)

    # Job done - process results
    output = slurm.get_job_output(job_id)
    print(f"Results: {output}")

    slurm.close()


# ============================================================================
# Example 2: Submit multiple jobs and monitor all concurrently
# ============================================================================

async def example_multiple_jobs():
    """Submit and monitor multiple jobs at once"""
    slurm = AsyncSLURMJob()

    jobs = []

    # Submit 3 jobs with different durations
    for i, duration in enumerate([10, 20, 15]):
        script = f"sleep {duration} && echo 'Job {i} finished'"
        job_id = slurm.submit_job(script, cpus=1, mem='1G')
        jobs.append(job_id)

    # Monitor all jobs concurrently
    tasks = [slurm.monitor_job(jid, poll_interval=3) for jid in jobs]
    await asyncio.gather(*tasks)

    print("All jobs completed!")
    slurm.close()


# ============================================================================
# Example 3: Do work while waiting, then finish when job is done
# ============================================================================

async def local_preprocessing():
    """Simulate preprocessing data locally"""
    print("[Local] Preprocessing data...")
    await asyncio.sleep(5)
    print("[Local] Data ready for upload")
    return {"data": "processed"}

async def local_postprocessing(job_output):
    """Simulate processing results after job completes"""
    print("[Local] Postprocessing results...")
    await asyncio.sleep(3)
    print(f"[Local] Final results processed: {job_output[:50]}...")

async def example_workflow():
    """Full workflow: preprocess, submit, monitor, postprocess"""
    slurm = AsyncSLURMJob()

    # Step 1: Preprocess locally
    data = await local_preprocessing()

    # Step 2: Submit job
    script = f"echo 'Processing {data}' && sleep 20 && echo 'Done'"
    job_id = slurm.submit_job(script, cpus=4, mem='4G')

    # Step 3: Monitor job (while potentially doing other things)
    await slurm.monitor_job(job_id, poll_interval=5)

    # Step 4: Get results and postprocess
    output = slurm.get_job_output(job_id)
    await local_postprocessing(output)

    slurm.close()


# ============================================================================
# Example 4: Monitor with timeout
# ============================================================================

async def example_with_timeout():
    """Monitor job but timeout if it takes too long"""
    slurm = AsyncSLURMJob()

    script = "sleep 100 && echo 'Done'"
    job_id = slurm.submit_job(script)

    try:
        # Wait max 30 seconds for job to complete
        await asyncio.wait_for(
            slurm.monitor_job(job_id, poll_interval=5),
            timeout=30
        )
        print("Job completed in time!")
    except asyncio.TimeoutError:
        print(f"Job {job_id} is taking too long, continuing anyway...")
        # Could cancel job here if needed: scancel {job_id}

    slurm.close()


# ============================================================================
# Example 5: Pipeline - finish job 1, then submit job 2
# ============================================================================

async def example_pipeline():
    """Chain multiple jobs - next job depends on previous"""
    slurm = AsyncSLURMJob()

    # Job 1: Generate data
    job1_script = "echo 'dataset_v1.txt' > ~/data_file.txt"
    job1_id = slurm.submit_job(job1_script, cpus=2)
    print("Job 1: Generating data...")
    await slurm.monitor_job(job1_id)

    # Job 2: Process the data (depends on job 1)
    job2_script = "cat ~/data_file.txt && echo 'processed'"
    job2_id = slurm.submit_job(job2_script, cpus=4)
    print("Job 2: Processing data...")
    await slurm.monitor_job(job2_id)

    # Get final results
    output = slurm.get_job_output(job2_id)
    print(f"Pipeline complete! Final output: {output}")

    slurm.close()


# ============================================================================
# Example 6: Monitor job while doing periodic local tasks
# ============================================================================

async def periodic_local_task():
    """Do something locally every 10 seconds"""
    count = 0
    while True:
        count += 1
        print(f"[Local] Periodic task execution #{count}")
        await asyncio.sleep(10)

async def example_with_background_work():
    """Monitor SLURM job while doing periodic local work"""
    slurm = AsyncSLURMJob()

    script = "sleep 25 && echo 'Remote computation done'"
    job_id = slurm.submit_job(script, cpus=2)

    # Start background task
    local_task = asyncio.create_task(periodic_local_task())

    # Monitor job
    await slurm.monitor_job(job_id, poll_interval=5)

    # Job done - cancel background work
    local_task.cancel()
    try:
        await local_task
    except asyncio.CancelledError:
        print("[Local] Background work cancelled - job is done!")

    slurm.close()


# ============================================================================
# Run examples
# ============================================================================

async def main():
    print("Choose an example:")
    print("1. Simple submit and monitor")
    print("2. Multiple jobs concurrently")
    print("3. Full workflow (pre + post processing)")
    print("4. Monitor with timeout")
    print("5. Job pipeline (chained jobs)")
    print("6. Background work while monitoring")

    choice = input("\nEnter choice (1-6): ").strip()

    examples = {
        '1': example_simple,
        '2': example_multiple_jobs,
        '3': example_workflow,
        '4': example_with_timeout,
        '5': example_pipeline,
        '6': example_with_background_work,
    }

    if choice in examples:
        await examples[choice]()
    else:
        print("Invalid choice")


if __name__ == '__main__':
    asyncio.run(main())
