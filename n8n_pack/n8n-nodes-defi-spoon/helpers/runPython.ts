import { spawn } from 'child_process';

export function runPython(
	pythonBin: string,
	code: string,
	inputJson: any,
): Promise<any> {
	return new Promise((resolve, reject) => {

		const py = spawn(pythonBin, ['-'], { stdio: ['pipe', 'pipe', 'pipe'] });

		let stdout = '';
		let stderr = '';

		py.stdout.on('data', (data) => (stdout += data.toString()));
		py.stderr.on('data', (data) => (stderr += data.toString()));

		py.on('close', (codeExit) => {
			if (codeExit !== 0) {
				return reject(new Error(`Python error: ${stderr}`));
			}

			try {
				resolve(JSON.parse(stdout));
			} catch {
				reject(new Error(`Invalid JSON from Python: ${stdout}`));
			}
		});

		py.stdin.write(`
import json
input_data = json.loads('''${JSON.stringify(inputJson)}''')

${code}
`);
		py.stdin.end();
	});
}
