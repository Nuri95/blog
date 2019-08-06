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

function sendReply(commentid) {
    var $replyForm = $('.reply-form-' + commentid);
    var postId = $('.form-comment').data('post');
    var body = $replyForm.find('.comment-body').val();
    $.post('/comment/new/', {post_id: postId, comment_id: commentid, body: body}, function (r) {
        console.log(r);

        $replyForm.parents('.child-comments').find('.col-12').prepend([
            '<div class="row">',
            '    <div class="col ml-5 mt-3">',
            '        <div class="child-comment">',
            '            <div class="row">',
            '                <div class="comment-author col-3">',
            '                    <a href="/user-posts/' + r.author.id + '/">' + r.author.username + '</a>',
            '                </div>',
            '                <div class="comment-time col-4">' + r.date + '</div>',
            '                <div class="offset-1 col-4">',
            '                    <a href="#" class="form-comment-delete pull-right" data-id="' + r.author.id + '">Удалить</a>',
            '                </div>',
            '            </div>',
            '            <div class="row">',
            '                <div class="comment-body col">' + r.body + '</div>',
            '            </div>',
            '        </div>',
            '    </div>',
            '</div>'
        ].join('\n'));

        $replyForm.remove();

    });
}

function replyComment(commentid, e) {
    var $replyForm = $('.reply-form-' + commentid);

    if ($replyForm.length === 0) {
        $(e.target).parents('.post-comment').find('.child-comments').prepend([
            '<div class="row reply-form-' + commentid + '" style="width: 100%;">',
            '   <input class="col-9 comment-body reply-comment-input" type="text" />',
            '   <button class="col-2 btn btn-info reply-send" data-id="' + commentid + '">Отправить</button>',
            '</div>'
        ].join('\n'));
        $replyForm = $('.reply-form-' + commentid);
    }

    attachSendReply($replyForm);
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
         console.log(xhr);
         xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
     }
});

function attachPostDelete() {
    $('.remove-post').click(function () {
       var $this = $(this);
            bootbox.confirm("Вы хотите удалить?", function (result) {

                if (result) {
                    removePost($this.data('id'));
                    return false;
                }
            });
            return false;
    });
}


function attachCommentDelete($container) {
    $container.find('.comments').on('click', '.form-comment-delete', function () {
        var $this = $(this);
        removeComment($this.data('id'));
        return false;
    });
}

function attachCommentReply($container) {
    $container.find('.comments').on('click', '.form-comment-reply', function (e) {
        var $this = $(this);
        replyComment($this.data('id'), e);
        return false;
    });
}

function attachSendReply($container) {
    $container.on('click', '.reply-send', function () {
        var $this = $(this);
        sendReply($this.data('id'));
        return false;
    });
}

function attachLike($container) {
      $container.find('.like').click(function() {
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
}

function attachComment($container) {
    $container.find('.form-comment').submit(function () {
        var $this = $(this);
        var postId = $this.data('post');
        var body = $this.find('.comment-body').val();

        $.post('/comment/new/', {post_id: postId, body: body}, function (r) {
            console.log(r);
            $container.find('.comments').prepend(
                [
                    '<div class="post-comment">',
                    '   <div class="row">',
                    '       <div class="comment-author col-3">',
                    '           <a href="/user-posts/' + r.author.id + '/">' + r.author.username + '</a>',
                    '       </div>',
                    '       <div class="comment-time col-4">' + r.date + '</div>',
                    '       <div class="offset-1 col-4">',
                    '           <a href="#" class="form-comment-delete pull-right" data-id="' + r.id + '">Удалить</a>',
                    '           <a href="#" class="form-comment-reply mr-2 pull-right" data-id="' + r.id + '">Ответить</a>',
                    '       </div>',
                    '   </div>',
                    '   <div class="row">',
                    '       <div class="comment-body col">' + r.body + '</div>',
                    '   </div>',
                    '</div>'
                ].join('\n')
            );
            $this.find('.comment-body').val('');
        });
        return false;
    });
}

function PostView($container) {
    attachCommentDelete($container);
    attachCommentReply($container);
    attachLike($container);
    attachComment($container);
}

function getRecent() {
    var encoded_posts;
    if (encoded_posts = localStorage.getItem('posts')){
        try {
            return JSON.parse(encoded_posts);
        }catch (e) {
            return [];
        }
    }else {
        return [];
    }
}

function rememberPost(post_id, title) {
     var posts = getRecent();
     var alreadyExists = $.map(posts, function (post, index) {
         if (post_id === post.id)
             return index;
     });
     if (alreadyExists.length){
         posts.splice(alreadyExists[0], 1);
     }
     posts.push({"id":post_id, "title": title});
     if (posts.length > 10){
         posts.shift();
     }
     localStorage.setItem('posts', JSON.stringify(posts));

}
function drawRecentPosts($container) {
    $container.html(
        $.map(getRecent().reverse(), function (post) {
              return '<li class="nav-item ">'+
                        '<a class="nav-link" href="/post/'+post.id+'/">'+post.title+
                        '</a>'+
                    '</li>';
        }).join(' ')
    );
}

