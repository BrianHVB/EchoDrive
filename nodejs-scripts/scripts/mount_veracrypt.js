#!/usr/bin/env node

const shell = require('shelljs');
const program = require('commander');
const helpers = require('./helpers');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

program
	.version('0.1.0')
	.usage('[options] <partition> <mount-point>')
	.arguments('<partition> <mount-point>')
	.option('--password <password>', 'The decryption password')
	.option('-p, --pass <entry-name>', 'Lookup the password for <entry-name> from the pass program')
	.action(mount)
	// .option('-P, --pineapple', 'Add pineapple')
	// .option('-b, --bbq-sauce', 'Add bbq sauce')
	// .option('-c, --cheese [type]', 'Add the specified type of cheese [marble]', 'marble')
	.parse(process.argv);


function mount(partition, mountPoint, opts) {
	const name = program.name();

	if (!helpers.isRoot()) {
		console.error("Root permission required. Try running this command with the 'sudo' prefix");
		return;
	}


	if (!opts.password === !opts.pass) {
		console.error(`You must include either the -pass or -password flags. Try ${name} --help for more info`);
		return;
	}

	let password = null;
	if (opts.pass) {
		getPasswordFromPass(opts.pass)
			.then(password => {
				console.log(`password is: ${password}`)
			})


	}


}

async function getPasswordFromPass(entry_name) {
	let stdout, stderr = null;
	try {
		({stdout, stderr} = await exec(`pass ${entry_name}`, {silent: true}));
	}
	catch(err) {
		console.log(err.stderr.trim());
		return null;
	}


	if (stderr) {
		const errorsToIgnore=[
			"gpg: WARNING"
		];

		let ignoreError = false;
		errorsToIgnore.forEach(errorSnippet => {
			if (stderr.includes(errorSnippet)) {
				ignoreError = true;
			}
		});

		if (!ignoreError) {
			console.error(stderr.trim());
			return null;
		}

	}
	return stdout.trim();
}


