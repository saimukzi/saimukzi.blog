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
    var moreArticleId = await getMoreArticleId_promise();
    if (moreArticleId == null) {
        loadMore_moreAvailable = false;
        return;
    }
    var moreArticleData = await getArticleData_promise(moreArticleId);
    var moreArticle = $('#load_article_template').clone();
    moreArticle.attr('id', 'load_article_' + loadMore_nextId);
    moreArticle.html(moreArticleData['content']);
    moreArticle.insertBefore('#article_end');
    loadMore_nextId += 1;
    return;
}

var loadMore_doneArticleIdSet = new Set();
loadMore_doneArticleIdSet.add(ARTICLE_META['id']);
var loadMore_articleIdList = [];
var loadMore_tagIdList = null;
async function getMoreArticleId_promise() {
    console.log('getMoreArticleId_promise');
    while(true){
        while (loadMore_articleIdList.length > 0) {
            var ret = loadMore_articleIdList.shift();
            if (loadMore_doneArticleIdSet.has(ret)) continue;
            loadMore_doneArticleIdSet.add(ret);
            return ret;
        }
        if (loadMore_tagIdList == null) {
            loadMore_tagIdList = ARTICLE_META['tags'];
        }
        if (loadMore_tagIdList.length <= 0) {
            return null;
        }
        var tagId = loadMore_tagIdList.shift();
        var tagData = await getTagData_promise(tagId);
        loadMore_articleIdList = tagData['article_id_list'];
    }
}

async function getArticleData_promise(articleId) {
    console.log('getArticleData_promise', articleId);
    var articleDbPath = getDbPath('article.'+articleId);
    var retDict = {
        'meta': await getJson_promise(articleDbPath + '/meta.json'),
        'content': await getTxt_promise(articleDbPath + '/content.txt'),
    };
    return retDict;
}

function getTagData_promise(tagId) {
    return getJson_promise('/tags/' + tagId + '.json');
}

var json_cache = {};
function getJson_promise(url) {
    url = CONFIG['base_url'] + url;
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
    var url = CONFIG['base_url'] + url;
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
    return CONFIG['base_url'] + '/db/' + keyHash.substring(0, 2) + '/' + keyHash.substring(2, 4) + '/' + keyHash;
}