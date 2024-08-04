$(document).ready(function() {
    detectBottomAndLoadMore();
    $(window).on('resize', detectBottomAndLoadMore);
});

addEventListener('scroll', () => {
    detectBottomAndLoadMore();
});

var detectBottomAndLoadMoreBusy = false;
function detectBottomAndLoadMore() {
    if (detectBottomAndLoadMoreBusy) {
        return;
    }
    detectBottomAndLoadMoreBusy = true;
    _detectBottomAndLoadMore_promise().catch(function(e) {
        console.error(e);
    }).finally(function() {
        detectBottomAndLoadMoreBusy = false;
    });
}
async function _detectBottomAndLoadMore_promise() {
    while(true){
        console.log('_detectBottomAndLoadMore');
        if (!getIsBottom()) return;
        if (!loadMore_moreAvailable) return;
        await loadMore_promise();
    }
}

var loadMore_busy = false;
async function loadMore_promise() {
    console.log('loadMore');
    if (loadMore_busy) return;
    loadMore_busy = true;
    try {
        return await _loadMore_promise();
    } finally {
        loadMore_busy = false;
    }
}

var loadMore_moreAvailable = true;
var loadMore_nextId = 0; // TODO: remove me
async function _loadMore_promise() {
    console.log('_loadMore_promise')
    if (!loadMore_moreAvailable) return;
    var moreBlogId = await getMoreBlogId_promise();
    if (moreBlogId == null) {
        loadMore_moreAvailable = false;
        return;
    }
    var moreBlogData = await getBlogData_promise(moreBlogId);
    var moreBlog = $('#load_blog_template').clone();
    moreBlog.attr('id', 'load_blog_' + loadMore_nextId);
    moreBlog.find('.blog_title').text(moreBlogData['meta']['title']);
    moreBlog.find('.blog_content').html(moreBlogData['content']);
    moreBlog.insertBefore('#blog_end');
    loadMore_nextId += 1;
    return;
}

var loadMore_doneBlogIdSet = new Set();
loadMore_doneBlogIdSet.add(BLOG_META['id']);
var loadMore_blogIdList = [];
var loadMore_tagIdList = null;
async function getMoreBlogId_promise() {
    console.log('getMoreBlogId_promise');
    while(true){
        while (loadMore_blogIdList.length > 0) {
            var ret = loadMore_blogIdList.shift();
            if (loadMore_doneBlogIdSet.has(ret)) continue;
            loadMore_doneBlogIdSet.add(ret);
            return ret;
        }
        if (loadMore_tagIdList == null) {
            loadMore_tagIdList = BLOG_META['tags'];
        }
        if (loadMore_tagIdList.length <= 0) {
            return null;
        }
        var tagId = loadMore_tagIdList.shift();
        var tagData = await getTagData_promise(tagId);
        loadMore_blogIdList = tagData['blog_id_list'];
    }
}

async function getBlogData_promise(blogId) {
    console.log('getBlogData_promise', blogId);
    var blogDbPath = getDbPath('article.'+blogId);
    var retDict = {
        'meta': await getJson_promise(joinPath([blogDbPath, 'meta.json'])),
        'content': await getTxt_promise(joinPath([blogDbPath, 'content.txt'])),
    };
    return retDict;
}

function getTagData_promise(tagId) {
    var url = joinPath([CONFIG['base_url'], 'tags', tagId + '.json']);
    return getJson_promise(url);
}

var json_cache = {};
function getJson_promise(url) {
    return new Promise(function(resolve, reject) {
        if (json_cache[url] != null) {
            resolve(json_cache[url]);
            return;
        }
        $.getJSON(url, function(data) {
            json_cache[url] = data;
            resolve(data);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            reject(errorThrown);
        });
    });
}

var txt_cache = {};
function getTxt_promise(url) {
    return new Promise(function(resolve, reject) {
        if (txt_cache[url] != null) {
            resolve(txt_cache[url]);
            return;
        }
        $.get(url, function(data) {
            txt_cache[url] = data;
            resolve(data);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            reject(errorThrown);
        });
    });
}

function getIsBottom() {
  return (window.innerHeight*1.5) + window.scrollY >= document.body.offsetHeight;
}

function getDbPath(key) {
    console.log('getDbPath', key);
    var keyHash = md5(key);
    return joinPath([CONFIG['base_url'], 'db', keyHash.substring(0, 2), keyHash.substring(2, 4), keyHash]);
}

function joinPath(v) {
    ret = '';
    for (var i = 0; i < v.length; i++) {
        if (v[i] == '') continue;
        if ((ret != '') && (ret[ret.length-1] != '/')) {
            ret += '/';
        }
        ret += v[i];
    }
    return ret;
}