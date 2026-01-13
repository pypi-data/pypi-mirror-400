import json

import paramiko

cpus = 4
mem = '4G'
time = '00:30:00'


def get_genomes(location):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'Waiting to connect...')
    ssh.connect('negishi.rcac.purdue.edu', username='ddeemer')
    print(f'Connected!\nls -lah {location}')
    stdin, stdout, stderr = ssh.exec_command(f'ls -lah {location}')
    output = stdout.read().decode()
    error = stderr.read().decode()
    ssh.close()

    if error:
        print(f'Error: {error}')

    # Split output into lines and filter out empty lines
    files = [line.strip() for line in output.split('\n') if line.strip()]
    print(f'Found files...\n{files}')
    return files


def submit_biotools_job(script_content, nodes=1, cpus=4, mem='4G', time='00:30:00'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'Waiting to connect...')
    ssh.connect('negishi.rcac.purdue.edu', username='ddeemer')
    print(f'Connected!')
    return 'This all worked big dawg!'


def submit_slurm_job(script_content, nodes=1, cpus=4, mem='4G', time='00:30:00'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'Waiting to connect...')
    ssh.connect('negishi.rcac.purdue.edu', username='ddeemer')
    print(f'Connected!')

    stdin, stdout, stderr = ssh.exec_command('touch im-here.flag')
    # stdin, stdout, stderr = ssh.exec_command('touch ~/myfile2.txt')

    # Create SLURM script
    slurm_script = f"""#!/bin/bash
#SBATCH -A lindems
#SBATCH --partition=cpu
#SBATCH --nodes={nodes}
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
#SBATCH --job-name=remote_job

source /etc/profile

{script_content}
    """
    # Write script and submit
    stdin, stdout, stderr = ssh.exec_command(
        f'cat > ~/job.sh << "EOF"\n{slurm_script}\nEOF\n'
        f'sbatch ~/job.sh'
    )

    job_id = stdout.read().decode().strip()
    try:
        stdin_content = stdin.read().decode().strip()
    except OSError:
        stdin_content = 'None'
    try:
        stderr_content = stderr.read().decode().strip()
    except OSError:
        stderr_content = 'None'
    print(f'Inside of submit_slurm_job:\nstdin: {stdin_content}\nstdout: {job_id},\nstderr: {stderr_content}\n')
    ssh.close()
    # Extract just the job number (sbatch returns "Submitted batch job 12345")
    if "Submitted batch job" in job_id:
        job_id = job_id.split()[-1]
    return job_id


def check_slurm_job_status(job_id):
    """
    Check the status of a SLURM job
    Returns: dict with status info (state, elapsed_time, etc.)
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('negishi.rcac.purdue.edu', username='ddeemer')

    # Use squeue to check if job is running/pending
    stdin, stdout, stderr = ssh.exec_command(f'squeue -j {job_id} --format="%T %M %j %a %l" --noheader')
    squeue_output = stdout.read().decode().strip()

    if squeue_output:
        # Job is still in queue (PENDING or RUNNING)
        parts = squeue_output.split()
        state = parts[0] if len(parts) > 0 else "UNKNOWN"
        elapsed = parts[1] if len(parts) > 1 else "0:00"
        job_name = parts[2] if len(parts) > 2 else "0:00"
        account = parts[3] if len(parts) > 3 else "0:00"
        limit = parts[4] if len(parts) > 4 else "0:00"
        ssh.close()
        return {"state": state, "elapsed_time": elapsed, "job_name": job_name, "account": account, "time limit": limit, "exists": True}

    # Job not in queue, check sacct for completed/failed jobs
    stdin, stdout, stderr = ssh.exec_command(f'sacct -j {job_id} --format=JobName,State,Elapsed --noheader | head -1')
    sacct_output = stdout.read().decode().strip()

    ssh.close()

    if sacct_output:
        parts = sacct_output.split()
        job_name = parts[0] if len(parts) > 0 else "UNKNOWN"
        state = parts[1] if len(parts) > 1 else "UNKNOWN"
        elapsed = parts[2] if len(parts) > 2 else "0:00"
        return {"job_name": job_name, "state": state, "elapsed_time": elapsed, "exists": True}

    return {"state": "NOT_FOUND", "elapsed_time": "0:00", "exists": False}


script_content = "echo 'hello motto' > ~/newfile-from-paramiko.txt"

if __name__ == '__main__':
    submit_slurm_job(script_content)