function request(type, url, successCallback, failCallback) {
    var request = new XMLHttpRequest();

    request.open(type, url, true);
    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    request.onreadystatechange = function () {
        if (request.readyState !== 4)
            return;
        if (request.status !== 200)
            failCallback();
        else
            successCallback();
    };
    request.send();
}

function removePost(postid) {
    request('DELETE', '/delete/' + postid + '/', function () {
        document.location.reload();
    }, function () {
        alert('Ошибка удаления');
    });
}

function logout() {
    request('POST', '/logout/', function () {
        alert('Пока');
        document.location.href = '/'

    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function like(id) {
    console.log(id);
    $.ajax({
        type:"POST",
        url: 'http://127.0.0.1:8000/like/'+id+'/',
        success: function (response) {
            console.log(response)
        },
        error: function (a, b, c) {
            console.log(a, b, c)
        }

    });
}