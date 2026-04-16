class UserController {
    constructor(userService) {
        this.userService = userService;
    }

    destroy = async (req, res) => {
        try {
            await this.userService.deleteUser(req.params.id);
            res.send('Usuário deletado.');
        } catch (err) {
            res.status(500).send('Erro DB');
        }
    };
}

module.exports = UserController;
