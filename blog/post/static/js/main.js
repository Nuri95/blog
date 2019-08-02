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
    request('DELETE', '/post/' + postid + '/delete/', function () {
        document.location.reload();
    }, function () {
        alert('Ошибка удаления');
    });
}
function removeComment(commentid) {
    request('DELETE', '/comment/'+commentid + '/delete/', function () {
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


$(function() {
    $('.show-alert').click(function () {
       var $this = $(this);
            bootbox.confirm("Вы хотите удалить?", function (result) {

                if (result) {
                    removePost($this.data('id'));
                    return false;
                }
            });
            return false;
    });

    $(document).on('click', '.form-comment-delete', function () {
        var $this = $(this);
        removeComment($this.data('id'));
        return false;
    });

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
    
    $('.form-comment').submit(function () {
        var $this = $(this);
        var postId = $this.data('post');
        var body = $('#comment-body').val();

        $('#comment-body').val('');

        $.post('/comment/new/', { post_id: postId, body: body }, function (r) {
            console.log(r);
            $('#comments').prepend(
                $([
                    '<div class="post-comment">',
                    '   <div class="comment-author">',
                    '       <a href="/user-posts/' + r.author.id + '/">' + r.author.username + '</a>',
                    '   </div>',
                    '   <div class="comment-body">' + r.body + '</div>',
                    '   <div class="comment-time">' + r.date + '</div>',
                    '   <a href="#" class="form-comment-delete" data-id="'+r.id+'">Удалить</a>',
                    '</div>'
                ].join('\n'))
            );
        });
        return false;
    });
});
