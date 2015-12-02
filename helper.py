class Paginate(object):
    def __init__(self, page, pages, filters, prefix):
        self.page = page
        self.pages = pages
        self.url_prefix = Paginate.get_url(filters, prefix)

    @staticmethod
    def get_url(filters, prefix):
        url = prefix + '?'
        for key, val in filters.iteritems():
            if val:
                url += '%s=%s&' % (key, val)
        return url

    def list_pages(self, left_edge=2, left_current=2,
                   right_current=2, right_edge=2):
        yield ('Prev', Paginate.form_url(self.url_prefix, self.page - 1) \
                   if self.page != 1 else None)
        
        snap_left = left_edge + 2 * left_current
        snap_right = self.pages - right_current - 2 * right_edge + 1
        not_in = False
        for num in xrange(1, self.pages + 1):
            if num == self.page:
                yield (str(num), True)
                not_in = True
            elif num <= left_edge or num >= self.page - left_current or \
                 (self.page <= snap_left and num <= snap_left) or \
                 num >= self.pages - right_edge + 1 or \
                 num <= self.page + right_current or \
                 (self.page >= snap_right and num >= snap_right):
                yield (str(num), Paginate.form_url(self.url_prefix, num))
                not_in = True
            elif not_in:
                yield ('...', None)
                not_in = False

        yield('Next', Paginate.form_url(self.url_prefix, self.page + 1) \
                  if self.page != self.pages else None)

    @staticmethod
    def form_url(prefix, page):
        return prefix + 'page=' + str(page)

