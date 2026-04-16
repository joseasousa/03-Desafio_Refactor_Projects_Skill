function validateCheckout(body) {
    const checkout = {
        userName: body.usr,
        email: body.eml,
        password: body.pwd,
        courseId: body.c_id,
        cardNumber: body.card
    };

    if (!checkout.userName || !checkout.email || !checkout.password || !checkout.courseId || !checkout.cardNumber) {
        return { error: 'Bad Request' };
    }

    if (!String(checkout.email).includes('@')) {
        return { error: 'Bad Request' };
    }

    if (!Number.isInteger(Number(checkout.courseId))) {
        return { error: 'Bad Request' };
    }

    if (!/^\d{12,19}$/.test(String(checkout.cardNumber))) {
        return { error: 'Bad Request' };
    }

    return {
        value: {
            ...checkout,
            courseId: Number(checkout.courseId),
            cardNumber: String(checkout.cardNumber)
        }
    };
}

module.exports = validateCheckout;
