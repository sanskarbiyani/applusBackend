from django.contrib.auth.models import Group
from rest_framework import permissions
from ddmapp.models import List_Database, List_group_link

from users.models import NewUser, User_group_link




class IsLoggedInUser(permissions.BasePermission):
    # group_name for super admin
    # required_groups = ['admin']
    def has_object_permission(self, request, view, obj):
        # has_group_permission = _has_group_permission(request.user, self.required_groups)
        # if self.required_groups is None:
        #     return False
        print(obj)
        try:
            
            if User_group_link.objects.get(user=request.user.id,group__name=obj['group']):
                print(obj['group'])    
                return True
        except Exception as ex:
            print("Data Not Found")
            return False
        return True
# def _has_group_permission(user, required_groups):
#     print(user,required_groups['group'])

class IsUserHasPermission(permissions.BasePermission):
    # group_name for super admin

    def has_object_permission(self, request, view, obj):
        print("hello")
        # print(User_group_link.objects.get(user=request.user.id,group=obj['modelname']))
        return False


# # class IsAdminUser(permissions.BasePermission):
# #     # group_name for super admin
# #     required_groups = ['admin']

# #     def has_permission(self, request, view):
# #         has_group_permission = _has_group_permission(request.user, self.required_groups)
# #         return request.user and has_group_permission

# #     def has_object_permission(self, request, view, obj):
# #         has_group_permission = _has_group_permission(request.user, self.required_groups)
# #         return request.user and has_group_permission

# class IsAdminOrAnonymousUser(permissions.BasePermission):
#     message = {'errors': ['Permission Denied']}
#     # required_groups = ['admin', 'anonymous']

#     def has_permission(self, request, view):
        
#         # print(List_Database.objects.get(modelname=request.data['list'],created_by = NewUser.objects.get(user_name = request.user).id))
        
#         try:
#             print(request.data['list'])
#             try:
#                 if List_Database.objects.get(modelname=request.data['list'],created_by = NewUser.objects.get(user_name = request.user).id):
#                     return True
#             except Exception as ex:
#                 print("Data Not Found")
#                 return False
                
#             print("###")
#             # _has_group_permission(request.user, request.data[''])
#         except Exception as e:
#             print("Error")

        
#         return True
#         # has_group_permission = _has_group_permission(request.user, self.required_groups)
#         # return request.user and has_group_permission
#     def has_object_permission(self, request, view, obj):
#         print("Hello Ji")
#         print(request.data)

#         # try:
            
#         #     try:
#         #         if List_Database.objects.count(modelname=obj['list_name'],created_by = NewUser.objects.get(user_name = request.user).id):
#         #             return True
#         #     except Exception as ex:
#         #         print("Data Not Found")
#         #         return False
                
#         #     print("###")
#         #     # _has_group_permission(request.user, request.data[''])
#         # except Exception as e:
#         #     print("Error")
#         # return True