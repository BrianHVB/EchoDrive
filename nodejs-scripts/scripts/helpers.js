module.exports = {
	isRoot() {
		const uid = process.getuid();
		return (uid === 0)
	},

};