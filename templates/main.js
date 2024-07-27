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
    try {
        _detectBottomAndLoadMore();
    } catch (e) {
        console.error(e);
    }
    detectBottomAndLoadMoreBusy = false;
}
function _detectBottomAndLoadMore() {
  while (getIsBottom() && loadMore_moreAvailable) {
    loadMore();
  }
}

var loadMore_moreAvailable = true;
var loadMore_nextId = 0; // TODO: remove me
function loadMore() {
    console.log('loadMore');
    if (!loadMore_moreAvailable) return;
    // TODO: implement me
    var more_article = $('#load_article_template').clone();
    more_article.attr('id', 'load_article_' + loadMore_nextId);
    more_article.text('Article ' + loadMore_nextId);
    more_article.insertBefore('#article_end');
    loadMore_nextId += 1;
}

function getIsBottom() {
  return (window.innerHeight*1.5) + window.scrollY >= document.body.offsetHeight;
}
