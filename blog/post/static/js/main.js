function request(type, url, successCallback, failCallback) {
    var x = new XMLHttpRequest();

    x.open(type, url, true);
    x.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    x.onreadystatechange = function () {
        if (x.readyState !== 4)
            return;
        if (x.status !== 200)
            if (failCallback)
                failCallback();
            else if (successCallback)
                successCallback();
    };
    x.send();
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

function attachMyPosts() {
    var urlParams = new URLSearchParams(window.location.search);
    var checkbox = document.getElementById('my_posts');

    if (urlParams.has('my') && (+urlParams.get('my') > 0)) {
        checkbox.checked = true;
    }
    checkbox.onchange = function () {
        if (this.checked) {
            urlParams.set('my', '1');
        } else {
            urlParams.delete('my');
        }
        urlParams.delete('page');
        document.location.search = urlParams.toString();
    }

}

function attachDataPage() {
    var click_link = function () {
        var urlParams = new URLSearchParams(window.location.search);
        urlParams.set('page', this.dataset.page);
        document.location.search = urlParams.toString();
        return false;
    };
    Array.prototype.forEach.call(document.getElementsByClassName('page-link'), function (link) {
        link.onclick = click_link;
    });
}