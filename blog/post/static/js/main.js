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

$.ajaxSetup({
     beforeSend: function(xhr) {
         xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
     }
});
//
// function like(id) {
//     $.ajax({
//         type:"POST",
//         url: 'http://127.0.0.1:8000/like/' + id + '/',
//
//         success: function (response) {
//             $('#like-count-' + id).text(response.totalLikes);
//             var $btn = $('#like-' + id);
//             $btn.siblings('.count_like').text(response.totalLikes);
//             if (response.isLiked){
//                 $btn.addClass('liked');
//             } else {
//                 $btn.removeClass('liked');
//             }
//
//         },
//         error: function (a, b, c) {
//             console.log(a, b, c)
//         }
//
//     })
// }

$(function() {
    $('.like').click(function() {
        var $this = $(this);
        var id = $this.data('id');

        $.post('/like/' + id + '/', function(response) {
            $('#like-count-' + id).text(response.totalLikes);

            if (response.isLiked) {
                $this.addClass('liked');
            } else {
                $this.removeClass('liked');
            }
        });
    });
});
