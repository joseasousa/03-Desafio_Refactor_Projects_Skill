class UserService {
    constructor(userRepository) {
        this.userRepository = userRepository;
    }

    deleteUser(id) {
        return this.userRepository.deleteWithRelatedData(id);
    }
}

module.exports = UserService;
