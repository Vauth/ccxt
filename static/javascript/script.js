function Alert(color, text) {
    const alertBox = document.getElementById('custom-alert');
    alertBox.style.backgroundColor = "#EEF7FF";
    alertBox.style.color = color;
    alertBox.textContent = text;
    alertBox.classList.add('show');
    setTimeout(() => { alertBox.classList.remove('show') }, 2000);
}

function Visibility(item_id) {
    const item = $(`#${item_id}`);
    if (item.css('display') === 'none') {item.css('display', 'flex')}
    else {item.css('display', 'none')}
}

function Clear() {
    $('#charge-cards').empty();
    $('#valid-cards').empty();
    $('#invalid-cards').empty();
    $("#status-button").text("0");
    $('#charge_text').text("CHARGE");
    $('#valid_text').text("ALIVE");
    $('#invalid_text').text("DEAD");
}

$(document).ready(function() {
    let stopChecking = false;
    let liveLen = 0;
    let deadLen = 0;
    let chargeLen = 0;

    $('#status-button').on('click', function(e) {
        const mount = $("#status-button").text();
        Alert("#565e64", "Currently " + mount + " cards on deck.")
    });

    $('#card-form').on('submit', function(e) {
        e.preventDefault();
        stopChecking = false; Clear()
        chargeLen = 0; liveLen = 0; deadLen = 0;
        const cardNumbers = $('#card_numbers').val().trim().split(/\s+/);
        if (cardNumbers.length === 1 && cardNumbers[0] === "") {
            return Alert("#c82333", "No credit card found.")
        }
        Alert("#277EE2", "Started checking " + cardNumbers.length + " cards ...")
        $("#status-button").text(cardNumbers.length);
        cardNumbers.forEach(card => {
            if (stopChecking) return;
            $.ajax({
                type: 'POST',
                url: '/check_card',
                contentType: 'application/json',
                data: JSON.stringify({ card_number: card }),
                success: function(response) {
                    if (!response.authed) {
                        stopChecking = true;
                        return Alert("#c82333", response.answer)
                    }
                    else if (response.charged) {
                        $('#charge-cards').append('<li class="list-group-item list-group-item-primary">' + response.answer + '</li>');
                        chargeLen += 1;
                        $('#charge_text').text(`CHARGE (${chargeLen})`);
                    }
                    else if (response.valid) {
                        $('#valid-cards').append('<li class="list-group-item list-group-item-secondary">' + response.answer + '</li>');
                        liveLen += 1;
                        $('#valid_text').text(`ALIVE (${liveLen})`);
                    } else {
                        $('#invalid-cards').append('<li class="list-group-item list-group-item-danger">' + response.answer + '</li>');
                        deadLen += 1;
                        $('#invalid_text').text(`DEAD (${deadLen})`);
                    }
                    if (liveLen+deadLen+chargeLen === cardNumbers.length) {
                        Alert("#277EE2", "Checked all cards.")
                        const audio = new Audio('./static/sound/success.mp3');
                        audio.play();
                    }
                }
            });
        });
    });

    $('#stop-button').on('click', function() {
        Alert("#c82333", "Stopped checker.")
        stopChecking = true;
    });
});
