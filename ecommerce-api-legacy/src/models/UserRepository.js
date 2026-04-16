class UserRepository {
    constructor(database) {
        this.database = database;
    }

    findByEmail(email) {
        return this.database.get('SELECT id FROM users WHERE email = ?', [email]);
    }

    create({ name, email, passwordHash }) {
        return this.database.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
            name,
            email,
            passwordHash
        ]);
    }

    async deleteWithRelatedData(id) {
        await this.database.run('BEGIN TRANSACTION');

        try {
            const enrollments = await this.database.all('SELECT id FROM enrollments WHERE user_id = ?', [id]);

            for (const enrollment of enrollments) {
                await this.database.run('DELETE FROM payments WHERE enrollment_id = ?', [enrollment.id]);
            }

            await this.database.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
            const result = await this.database.run('DELETE FROM users WHERE id = ?', [id]);
            await this.database.run('COMMIT');
            return result;
        } catch (err) {
            await this.database.run('ROLLBACK');
            throw err;
        }
    }
}

module.exports = UserRepository;
