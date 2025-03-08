from werkzeug.utils import redirect

from SaleBook.models import Book, User, Category, Regulation, UserRole
from flask_admin.contrib.sqla import ModelView
from SaleBook import app, db, dao
from flask_login import current_user, logout_user
from flask_admin import Admin, BaseView, expose
from flask import request

admin = Admin(app=app, name='Quản trị nhà sách', template_mode='bootstrap4')


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class BookView(AdminView):
    column_list = ['name', 'category', 'author']


class CategoryView(AdminView):
    column_list = ['name', 'books']


class MyModelView(AdminView):
    column_list = ('name', 'value')
    form_widget_args = {
        'name': {
            'readonly': True
        }
    }
    can_create = False
    column_editable_list = ['value']


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')


from datetime import datetime


class StatsOnlineView(AuthenticatedView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        date = request.args.get('date')

        # Nếu date không rỗng, tách tháng và năm
        if date:
            year, month = map(int, date.split('-'))
        else:
            # Nếu không có input, lấy năm tháng hiện tại
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))

        report, total_revenue = dao.get_stats_online(year, month, kw)
        print(report)

        return self.render('admin/stats_online.html', stats=report, total_revenue=total_revenue)


class StatsOfflineView(AuthenticatedView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        date = request.args.get('date')

        # Nếu date không rỗng, tách tháng và năm
        if date:
            year, month = map(int, date.split('-'))
        else:
            # Nếu không có input, lấy năm tháng hiện tại
            year = int(request.args.get('year', datetime.now().year))
            month = int(request.args.get('month', datetime.now().month))

        report, total_revenue = dao.get_stats_store(year, month, kw)
        print(report)

        return self.render('admin/stats_store.html', stats=report, total_revenue=total_revenue)


admin.add_view(AdminView(User, db.session))
admin.add_view(BookView(Book, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(MyModelView(Regulation, db.session))

admin.add_view(StatsOnlineView(name='Doanh số bán online'))
admin.add_view(StatsOfflineView(name='Doanh số tại cửa hàng'))
admin.add_view(LogoutView(name='Đăng xuất'))
