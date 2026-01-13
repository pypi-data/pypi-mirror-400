from rest_framework import viewsets
from rest_framework import filters
from .serializers import *
from rest_framework.decorators import action
from django.db.models import F
from rest_framework.response import Response
from rest_framework import status
import importlib.util
from django.apps import apps
from .decorators import hasPermission, isPermited



class  FicheiroAPIView(viewsets.ModelViewSet):

    search_fields = ['id','ficheiro']
    filter_backends = (filters.SearchFilter,)
    serializer_class = FicheiroSerializer
    queryset = Ficheiro.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter().order_by('-id')
    # A implementaçao desse codigo faz com que nao se returne o full path de im ficheiro
    def retrieve(self, request, id, *args, **kwargs):
        try:
            transformer = self.get_object()
            entidade = FicheiroSerializer(transformer)
            return Response(entidade.data, status=status.HTTP_200_OK)
        except Http404:
            pass
        return Response( status=status.HTTP_404_NOT_FOUND)


    def destroy(self, request, id, *args, **kwargs):
        try:
            instance = self.get_object()
            DiscManegar.recoverSpace(instance.entidade.id, instance)
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    
    def list(self, request, *args, **kwargs):
        self._paginator = None
        queryset = self.filter_queryset(self.get_queryset().filter().order_by('-id'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def update(self, request,id,  *args, **kwargs):
        transformer = self.get_object()
        entidade = FicheiroSerializer(transformer, data=request.data)
        if entidade.is_valid(raise_exception=True):
            entidade.save()
            return Response(entidade.data, status=status.HTTP_201_CREATED)
        else:
            return Response(entidade.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')
        request.data['entidade'] = entidade_id
        request.data['sucursal'] = sucursal_id
        uploaded_file = request.FILES['ficheiro']
        
        if entidade_id:
            DiscManegar.freeSpace(entidade_id, request.FILES['ficheiro'])

        request.data['size'] = uploaded_file.size

        ficheiro = FicheiroGravarSerializer(data=request.data)
        if ficheiro.is_valid(raise_exception=True):
            ficheiro.save()
            ficheiro = FicheiroSerializer(Ficheiros.objects.get(id=ficheiro.data['id']))
            return Response(ficheiro.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ficheiro.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(
        detail=True,
        methods=['GET'],
    )
    def sucursals(self, request, id):
        sucursals = FicheiroSerializer.objects.filter(entidade__id=id)
        suc = []
        for sucursal in sucursals:
            try:
                suc.append({'id': sucursal.id, 'nome': sucursal.nome})
            except:
                pass
        return Response(suc)



class ModeloAPIView(viewsets.ModelViewSet):
    search_fields = ['id']
    filter_backends = (filters.SearchFilter,)
    serializer_class = ContentTypeSerializer
    queryset = ContentType.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter().order_by('app_label','model')
    
    def list(self, request, *args, **kwargs):
        self._paginator = None
        queryset = self.filter_queryset(self.get_queryset().filter().order_by('app_label', 'model'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InputAPIView(viewsets.ModelViewSet):
    search_fields = ['id','nome']
    filter_backends = (filters.SearchFilter,)
    serializer_class = InputSerializer
    queryset = Input.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        self._paginator = None
        return self.queryset.filter().order_by('nome')
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def strings(self, request, id, *args, **kwargs):
        r = []
        try:
            st = InputString.objects.filter(input__id=id)
            for i in st:
                string = StringSerializer(String.objects.get(id=i.string.id))
                r.append(string.data)
            return Response(r, status.HTTP_200_OK)
        except:
            return Response(r, status.HTTP_200_OK)
        
    @action(
        detail=True,
        methods=['POST'],
    )
    def addString(self, request, id):
        
        string = String.objects.create(texto=request.data['texto'])
        input = Input.objects.get(id=id)
        InputString.objects.create(string = string , input = input)
   
        per= {'id': string.id, 'nome': string.texto, 'nomeseparado':input.nome, 'alert_info': 'Permicao <b>' +string.texto + '</b> foi removido consucesso'}
        return Response(per,status.HTTP_201_CREATED )
    
    


class StringAPIView(viewsets.ModelViewSet):
    search_fields = ['id','texto']
    filter_backends = (filters.SearchFilter,)
    serializer_class = StringSerializer
    queryset = String.objects.all()
    lookup_field = "id"


    def get_queryset(self):
        self._paginator = None
        if (self.request.query_params.get('input')):
            r = []
            try:
                st = InputString.objects.filter(input__nome=self.request.query_params.get('input'))
                for i in st:
                    string = StringSerializer(String.objects.get(id=i.string.id))
                    r.append(string.data)
                return r
            except:
                return r
        else:
            return self.queryset.filter().order_by('texto')
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def inputs(self, request, id, *args, **kwargs):
        r = []
        try:
            st = InputString.objects.filter(string__id=id)
            for i in st:
                input = InputSerializer(Input.objects.get(id=i.input.id))
                r.append(input.data)
            return Response(r, status.HTTP_200_OK)
        except:
            return Response(r, status.HTTP_200_OK)
        
    @action(
        detail=True,
        methods=['POST'],
    )
    def addToInput(self, request, id):

        string = String.objects.get(id=id)
        input = Input.objects.get(id=request.data['id'])
        inpStr = InputString()
        inpStr.input = input
        inpStr.string = string
        inpStr.save()
    
        per= {'id': string.id, 'nome': string.texto, 'nomeseparado':input.nome, 'alert_info': 'Permicao <b>' +string.texto +  '</b> foi Adicionado consucesso'}
        return Response(per,status.HTTP_201_CREATED )


    @action(
        detail=True,
        methods=['POST'],
    )
    def removeFromInput(self, request, id):
        print(id,request.data['id'])
        InputString.objects.get(string__id = id , input__id = request.data['id']).delete()
        print(inpStr)
        string = String.objects.get(id=inpStr.string.id)
        input = Input.objects.get(id=inpStr.input.id)
    
        per= {'id': string.id, 'nome': string.texto, 'nomeseparado':input.nome, 'alert_info': 'Permicao <b>' +string.texto + '</b> foi removido consucesso'}
        return Response(per,status.HTTP_201_CREATED )


class  IdiomaAPIView(viewsets.ModelViewSet):
    paginator = None
    search_fields = ['id','nome']
    filter_backends = (filters.SearchFilter,)
    serializer_class = IdiomaSerializer
    queryset = Idioma.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter().order_by('nome')


    def retrieve(self, request, id, *args, **kwargs):
        try:
            transformer = self.get_object()
            idioma = IdiomaSerializer(transformer)
            return Response(idioma.data, status=status.HTTP_200_OK)
        except Http404:
            pass
        return Response( status=status.HTTP_404_NOT_FOUND)


    def destroy(self, request, id, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


    def update(self, request,id,  *args, **kwargs):
        transformer = self.get_object()

        idioma = IdiomaSerializer(transformer, data=request.data)
        if idioma.is_valid(raise_exception=True):
            idioma.save()
            add={'alert_success': '%-'+ request.data['nome'] +'-% foi actualizado com sucesso'}
            data = json.loads(json.dumps(idioma.data))
            data.update(add)

            return Response(data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(idioma.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        request.data['admin'] = request.user.id
        idioma = IdiomaSerializer(data=request.data)
        if idioma.is_valid(raise_exception=True):
            idioma.save()
            add = {'alert_success': '%-'+ request.data['nome'] +'-% foi criado com sucesso'}
            data = json.loads(json.dumps(idioma.data))
            data.update(add)

            return Response(data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(idioma.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioAPIView(viewsets.ModelViewSet):
    search_fields = ['id','username']
    filter_backends = (filters.SearchFilter,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        if (self.request.query_params.get('allPaginado')):
            return self.queryset.filter().order_by('id')
        else:
            self._paginator = None
            return self.queryset.filter().order_by('id')

    @action(
        detail=True,
        methods=['GET'],
    )
    def userEntidades(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        user = UserSerializer(user)
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')

        ar = []
        userEntidades = EntidadeUser.objects.filter(user__id=id, entidade__tipo_entidade__id=tipo_entidade_id)
        if (userEntidades):
            for userEntidade in userEntidades:
                entidade = Entidade.objects.get(id=userEntidade.entidade.id)
                entidade = EntidadeSerializer(entidade, context={'request': request})
                ar.append({'id': entidade.data['id'], 'tipoEntidade': entidade.data['tipo_entidade'],  'nome': entidade.data['nome'], 'created_at': entidade.data['created_at'].split('-')[0], 'logo': entidade.data['logo']['url']})
           

        return Response(ar, status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['GET'],
    )
    def logins(self, request, id, *args, **kwargs):
        userLogin = UserLogin.objects.filter(user_id = id).order_by('-data', 'hora')
        userLogins = UserLoginSerializer(userLogin, many=True)
        return Response(userLogins.data, status=status.HTTP_200_OK)
    
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def userSucursals(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        user = UserSerializer(user)
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')

        ar = []
        userSucursals = SucursalUser.objects.filter(user__id=id, sucursal__entidade__tipo_entidade__id=tipo_entidade_id, sucursal__entidade__id=entidade_id)
        if (userSucursals):
            for userSucursal in userSucursals:
                sucursal = Sucursal.objects.get(id=userSucursal.sucursal.id)
                sucursal = SucursalSerializer(sucursal)
                ar.append({'id': sucursal.data['id'], 'nome': sucursal.data['nome']})

        return Response(ar, status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['POST'],
    )
    def addUserSucursal(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')
        sucursal = Sucursal.objects.get(id= request.data['sucursal'])

        ar = []
        userSucursals = SucursalUser.objects.filter(user__id=id, sucursal__id= sucursal.id,  sucursal__entidade__tipo_entidade__id=tipo_entidade_id, sucursal__entidade__id=entidade_id)
        if (len(userSucursals) <= 1):
            su = SucursalUser()
            su.user = user
            su.sucursal  = sucursal
            su.save()
            # data = json.loads(json.dumps(paciente.data, cls=DjangoJSONEncoder))
        add = {'alert_success':  '<b>' + sucursal.nome+ '</b> foi adicionado com sucesso'}
            # data.update(add)
        return Response(add, status = status.HTTP_201_CREATED)
    
    @action(
        detail=True,
        methods=['POST'],
    )
    def removeUserSucursal(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')
        sucursal = Sucursal.objects.get(id= request.data['sucursal'])

        userSucursals = SucursalUser.objects.get(user__id=id, sucursal__id= sucursal.id, sucursal__entidade__tipo_entidade__id=tipo_entidade_id, sucursal__entidade__id=entidade_id)
        userSucursals.delete()
        add = {'alert_success': '<b>' + sucursal.nome+ '</b> foi removido com sucesso'}
        return Response(add, status = status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['GET'],
    )
    def userGrupos(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        user = UserSerializer(user)

        if self.request.query_params.get('sucursal') == 'nulo' or self.request.query_params.get('sucursal') == None:
            tipo_entidade_id = request.headers.get('ET')
            entidade_id = request.headers.get('E')
            sucursal_id = request.headers.get('S')
            grupo_id = request.headers.get('G')
        else:
            sucursal_id = self.request.query_params.get('sucursal')

        sucursalUserGroups = SucursalUserGroup.objects.filter(user__id=id, sucursal__id=sucursal_id)
        ar = []
        if (sucursalUserGroups):
            for sucursalUserGroup in sucursalUserGroups:
                group = Group.objects.get(id=sucursalUserGroup.group.id)
                ar.append({'id': group.id, 'name': group.name})

        if True:
            return Response(ar, status.HTTP_200_OK)
        return Response([], status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET'],
    )
    def userPermicoes(self, request, id, *args, **kwargs):
        user = User.objects.get(id=id)
        user = UserSerializer(user)
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')

        group_id = grupo_id
        sucursalUserGroup = SucursalUserGroup.objects.filter(user__id = id, sucursal__id = sucursal_id, group__id = group_id)
        
        per = []
        if (sucursalUserGroup):
            grupo = Group.objects.get(id=sucursalUserGroup[0].group.id)
            permissions = grupo.permissions.all()

            for permission in permissions:
                per.append({'id': permission.id, 'nome': permission.codename, 'nomeseparado': permission.name})

        if True:
            return Response(per, status.HTTP_200_OK)
        return Response([], status.HTTP_400_BAD_REQUEST)


    @action(
        detail=True,
        methods=['GET'],
    )
    def userPessoa(self, request, id, *args, **kwargs):

        pessoa = Pessoa.objects.get(user__id=id)
        pessoa = PessoaSerializer(pessoa)
        if pessoa:
            return Response(pessoa.data, status.HTTP_200_OK)
        return Response([], status.HTTP_400_BAD_REQUEST)


    @action(
        detail=True,
        methods=['POST'],
    )
    def removerPerfil(self, request, id ):
        user = User.objects.get(id=id)
        group_id = request.data['perfil']['id']
        sucursal_id = request.data['sucursal_id']
        sucursalUserGroups = SucursalUserGroup.objects.filter(user__id=id, sucursal__id=sucursal_id, group__id= group_id).first()
        sucursalUserGroups.delete()
        ar = []
        sucursalUserGroups = SucursalUserGroup.objects.filter(user__id=id, sucursal__id=sucursal_id)
        if (sucursalUserGroups):
            for sucursalUserGroup in sucursalUserGroups:
                group = Group.objects.get(id=sucursalUserGroup.group.id)
                ar.append({'id': group.id, 'name': group.name})
                # print(ar)

        if True:
            return Response(ar, status.HTTP_200_OK)
        return Response([], status.HTTP_400_BAD_REQUEST)


    @action(
        detail=True,
        methods=['POST'],
    )
    def adicionarPerfil(self, request, id):
        user = User.objects.get(id=id)
        group_id = request.data['perfil']['id']
        group = Group.objects.get(id = group_id)
        sucursal_id = request.data['sucursal_id']
        sucursal = Sucursal.objects.get(id=sucursal_id)
        sucursalUserGroups = SucursalUserGroup.objects.filter(user__id=id, sucursal__id=sucursal_id, group__id= group_id).first()

        if None==sucursalUserGroups:
            sucursalUserGroup = SucursalUserGroup()
            sucursalUserGroup.user = user
            sucursalUserGroup.group = group
            sucursalUserGroup.sucursal = sucursal
            sucursalUserGroup.save()
        sucursalUserGroups = SucursalUserGroup.objects.filter(user__id=id, sucursal__id=sucursal_id)

        ar = []
        if (sucursalUserGroups):
            for sucursalUserGroup in sucursalUserGroups:
                group = Group.objects.get(id=sucursalUserGroup.group.id)
                ar.append({'id': group.id, 'name': group.name})
                # print(ar)

        if True:
            return Response(ar, status.HTTP_200_OK)
        return Response([], status.HTTP_400_BAD_REQUEST)




class TipoEntidadeAPIView(viewsets.ModelViewSet):
    search_fields = ['id','nome']
    filter_backends = (filters.SearchFilter,)
    
    serializer_class =TipoEntidadeSerializer
    queryset =TipoEntidade.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        if (self.request.query_params.get('all')):
            return self.queryset.filter().order_by('ordem')
        else:
            self._paginator = None
            return self.queryset.filter(estado='Activo').order_by('ordem')
    
    

    @action(
        detail=True,
        methods=['GET'],
    )
    def user_entidades(self, request, id):
        entidades = Entidade.objects.filter(tipo_entidade__id=id)
        ent = []
        for entidade in entidades:

            try:
                entidadeUser = EntidadeUser.objects.get( entidade=entidade, user=request.user)
                if entidadeUser:
                    logo = FullPath.url(request, entidade.logo.name)
                    ent.append({'id': entidade.id, 'nome': entidade.nome, 'logo': logo})
            except:
                pass
        return Response(ent , status=status.HTTP_200_OK)


    @action(
        detail=True,
        methods=['GET'],
    )
    def entidades(self, request, id):
        entidades = Entidade.objects.filter(tipo_entidade__id = id)

        ent = []
        for entidade in entidades:
            try:
                logo = str(entidade)
                ent.append({'id': entidade.id, 'nome': entidade.nome})
            except:
                pass
        return Response(ent , status=status.HTTP_200_OK)
    

    @action(
        detail=True,
        methods=['GET'],
    )
    def downloadPermission(self, request, id):
        te = TipoEntidade.objects.get(id=id)
        groups = db.reference('Premissions').child(te.nome).get()
        for key, permissions in groups.items():
            try:
                g = Group.objects.get(name=key)
                te.groups.add(g)
            except:
                g = Group.objects.create(name=key)
                te.groups.add(g)

        for group in te.groups.all():
            datas = db.reference('Premissions').child(te.nome).child(group.name).get()
            gr = Group.objects.get(id=group.id)
            gr.permissions.clear()
            try:
                for permission in datas:
                    try:
                        p = Permission.objects.get(codename=permission['codename'])
                        gr.permissions.add(p)
                    except:

                        content_type, created = ContentType.objects.get_or_create(
                            model='downloaded',
                        )
                        custom_permission, created = Permission.objects.get_or_create(content_type= content_type, codename=permission['codename'], defaults={'name': permission['name']})
                        gr.permissions.add(custom_permission)
            except:
                pass
            gr.save()

            for entidade in Entidade.objects.filter(tipo_entidade_id=id):
                for g in te.groups.all():
                    entidade.groups.add(g)

        te = {'id': te.id, 'nome': te.nome, 'alert_success': 'Permicoes baixadas para<br><b>'+te.nome+'</b>'}
        
        return Response(te , status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def uploadPermission(self, request, id):
        te = TipoEntidade.objects.get(id=id)
        grupos ={}
        for group in te.groups.all():
            ref = db.reference('Premissions').child(te.nome)
            data = PermissionSerializer(group.permissions.all(), many=True).data
            grupos[group.name] = data
        ref.set(grupos)     
        te = {'id': te.id, 'nome': te.nome, 'alert_success': 'Permicoes actualizadas para<br><b>'+te.nome+'</b>'}
        
        return Response(te , status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['PUT'],
    )
    def perfilPut(self, request, id):
        group = Group.objects.get(id=request.data['id'])
        group.name = request.data['name']
        group.save()
        
        perfil = {'id': group.id, 'name': group.name, 'alert_success': 'Perfil <b>'+ group.name + ' </b> actualizado com sucesso'}
        return Response(perfil, status.HTTP_201_CREATED)


    @action(detail=True, methods=['POST'],)
    def perfilPost(self, request, id):
        tipoentidade = TipoEntidade.objects.get(id=id)        
        group = Group.objects.create(name=request.data['name'])
        tipoentidade.groups.add(group)
        for entidade in Entidade.objects.filter(tipo_entidade_id=id):
            entidade.groups.add(group)

        perfil = {'id': group.id, 'name': group.name, 'alert_success': 'Perfil <b>'+ group.name + ' </b> criado com sucesso'}
        return Response(perfil, status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['GET'],)
    def apps(self, request, id):
        tipoentidade = TipoEntidade.objects.get(id=id)        
        apps_ = []
        
        for app in apps.get_app_configs():
            apps_.append({'name': app.name, 'label': app.label, 'verbose': app.verbose_name })
            
        for app in dj_settings.INSTALLED_APPS:
            apps_.append(app)


        return Response(apps_, status.HTTP_200_OK)
    
    # @user_has_permission('view_entidade')
    @action(detail=True,methods=['GET'],)
    def menus(self, request, *args, **kwargs):
        transformer = self.get_object()
        ALL_MENUS = {}
        MENUS =[]
        for app in apps.get_app_configs():
            sidebar = None
            module_name = app.name + ".sidebar"
            if importlib.util.find_spec(module_name):
                sidebar = importlib.import_module(module_name)
            else:       
                continue

            if sidebar:
                MENU = {}
                MENU["app"] = app.label
                MENU["menu"] = sidebar.MENU
                MENU["icon"] = sidebar.ICON
                MENU["role"] = sidebar.ROLE
                MENU["submenu"] = []
                for submenu in sidebar.SUBMENUS:
                    MENU["submenu"].append(submenu) 

                MENUS.append(MENU)

        return Response(MENUS, status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def modelos(self, request, id):
        tipoentidade = TipoEntidade.objects.get(id=id)        
        modelos = []
        for modelo in tipoentidade.modelos.all():
           modelos.append({'id': modelo.id, 'model': modelo.model, 'app_label':  modelo.app_label })

        return Response(modelos, status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['POST'],
    )
    def addModelo(self, request, id):
        tipoentidade = TipoEntidade.objects.get(id=id)        
        modelo = ContentType.objects.get(id=request.data['id'])
        tipoentidade.modelos.add(modelo)
        for entidade in Entidade.objects.filter(tipo_entidade_id=id):
            entidade.modelos.add(modelo)
            
        modelo = {'id': modelo.id, 'model': modelo.model, 'alert_success': 'App <b>'+ modelo.model + ' </b> criado com sucesso'}
        return Response(modelo, status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST'],
    )
    def removeModelo(self, request, id):
        tipoentidade = TipoEntidade.objects.get(id=id)        
        modelo = ContentType.objects.get(id=request.data['id'])
        tipoentidade.modelos.remove(modelo)
        for entidade in Entidade.objects.filter(tipo_entidade_id=id):
            entidade.modelos.remove(modelo)

        modelo = {'id': modelo.id, 'model': modelo.model, 'alert_success': 'App <b>'+ modelo.model + ' </b> Removido com sucesso'}
        return Response(modelo, status.HTTP_201_CREATED)



class  EntidadeAPIView(viewsets.ModelViewSet):
    search_fields = ['id','nome']
    filter_backends = (filters.SearchFilter,)
    serializer_class = EntidadeSerializer
    queryset = Entidade.objects.all()


    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter().order_by('-id')

    def retrieve(self, request, *args, **kwargs):
        try:
            transformer = self.get_object()
            paciente = EntidadeSerializer(transformer, context={'request': request})
            return Response(paciente.data, status=status.HTTP_200_OK)
        except Http404:
            pass
        return Response(status=status.HTTP_404_NOT_FOUND)


    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        self._paginator = None
        queryset = self.filter_queryset(self.get_queryset().filter().order_by('-id'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request,  *args, **kwargs):

        transformer = self.get_object()

        entidade = EntidadeSerializer(transformer, data=request.data)
        if entidade.is_valid(raise_exception=True):
            entidade.save()
            return Response(entidade.data, status=status.HTTP_201_CREATED)
        else:
            return Response(entidade.errors, status=status.HTTP_400_BAD_REQUEST)



    def create(self, request, *args, **kwargs):
        
        tipo_entidade_id = request.headers.get('ET')
        entidade_id = request.headers.get('E')
        sucursal_id = request.headers.get('S')
        grupo_id = request.headers.get('G')
        if self.request.query_params.get('selfRegist') == 'self':
            request.data['tipo_entidade'] = tipo_entidade_id
            request.data['admin'] = request.user.id

        entidade = EntidadeGravarSerializer(data=request.data)

        if entidade.is_valid(raise_exception=True):
            entidadeSave = entidade.save()

            entidadeUser = EntidadeUser()
            entidadeUser.user = request.user
            entidadeUser.entidade = entidadeSave
            entidadeUser.save()

            tipoEntidade = TipoEntidade.objects.all().filter(id=entidadeSave.tipo_entidade.id).first()
            for group in tipoEntidade.groups.all():
                entidadeSave.groups.add(group)

            sucursal = Sucursal()
            sucursal.nome = entidadeSave.nome+' Sede'
            sucursal.entidade = entidadeSave
            sucursal.endereco = '...'
            sucursal.icon = '...'
            sucursal.label = '...'

            sucursal.save()

            sucursalUser = SucursalUser()
            sucursalUser.user = request.user
            sucursalUser.sucursal = sucursal
            sucursalUser.save()

            user = User.objects.all().filter(id=request.user.id).first()
            for group in tipoEntidade.groups.all():
                sucursal.groups.add(group)
                user.groups.add(group)

                sucursalUserGroup = SucursalUserGroup()
                sucursalUserGroup.group = group
                sucursalUserGroup.user = request.user
                sucursalUserGroup.sucursal = sucursal
                sucursalUserGroup.save()

            return Response(entidade.data, status=status.HTTP_201_CREATED)

        else:
            return Response(entidade.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET'],
    )
    def sucursals(self, request, *args, **kwargs):
        transformer = self.get_object()
        sucursals = Sucursal.objects.filter(entidade__id=transformer.id)
        suc = []
        for sucursal in sucursals:
            try:
                suc.append({'id': sucursal.id, 'nome': sucursal.nome, 'estado': sucursal.estado})
            except:
                pass
        return Response(suc)
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def modelos(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidade = Entidade.objects.get(id= transformer.id)        
        modelos = []
        for modelo in entidade.modelos.all():
           modelos.append({'id': modelo.id, 'model': modelo.model, 'app_label':  modelo.app_label })

        return Response(modelos, status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['GET'],
    )
    def modulos(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidade = Entidade.objects.get(id= transformer.id)        
        modulos = set()
        for modelo in entidade.modelos.all():
           modulos.add( modelo.app_label )

        return Response(modulos, status.HTTP_200_OK)

    
    @action(detail=True, methods=['POST'],)
    def addModelo(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidade = Entidade.objects.get(id=transformer.id)        
        modelo = ContentType.objects.get(id=request.data['id'])
        entidade.modelos.add(modelo)

        modelo = {'id': modelo.id, 'model': modelo.model, 'alert_info': 'App <b>'+ modelo.app_label + ' </b> criado com sucesso'}
        return Response(modelo, status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST'],
    )
    def removeModelo(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidade = Entidade.objects.get(id=transformer.id)        
        modelo = ContentType.objects.get(id=request.data['id'])
        entidade.modelos.remove(modelo)
        
        modelo = {'id': modelo.id, 'model': modelo.model, 'alert_info': 'App <b>'+ modelo.app_label + ' </b> Removido com sucesso'}
        return Response(modelo, status.HTTP_201_CREATED)


    @action(
        detail=True,
        methods=['GET'],
    )
    def perfils(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidade = Entidade.objects.get(id=transformer.id)

        perfils = []
        for group in entidade.groups.all():
            perfils.append({'id': group.id, 'name': group.name})
            
        perfils = sorted(perfils, key=lambda arguments : arguments['name'])

        return Response(perfils, status.HTTP_200_OK)    

    @action(
        detail=True,
        methods=['GET'],
    )
    def usuarios(self, request, *args, **kwargs):
        transformer = self.get_object()
        search = self.request.query_params.get('search')
        entidadeUsers = EntidadeUser.objects.filter(entidade__id=transformer.id, user__username__icontains = search, is_deleted = False  ).order_by('-user__username')
        page = self.paginate_queryset(entidadeUsers)
        serializer = EntidadeUserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


    @action(
        detail=True,
        methods=['POST'],
    )
    def addUser(self, request, *args, **kwargs):
        transformer = self.get_object()
        entidadeUser = EntidadeUser()
        entidadeUser.user = User.objects.get(id = request.data['user'])
        entidadeUser.entidade = Entidade.objects.get(id = transformer.id)
        
        if len(EntidadeUser.objects.filter(entidade__id=transformer.id, user = entidadeUser.user, is_deleted = False  )) < 1 :
            data = entidadeUser.save()
            adda = {"alert_seccess": "O usuario " +  entidadeUser.user.username + " adicionado com sucesso!"}
            return Response (adda, status=status.HTTP_201_CREATED)
            
        
        adda = {"alert_seccess": "O usuario " +  entidadeUser.user.username + " ja existe !"}
        return Response(adda, status.HTTP_201_CREATED)
    

    @action(
        detail=True,
        methods=['DELETE'],
    )
    def removeUser(self, request, *args, **kwargs):
        transformer = self.get_object()
        try:
            entidadeUser = EntidadeUser.objects.filter(entidade__id=transformer.id, is_deleted = False, user__id = request.query_params.get('user') ).first()
            entidadeUser.is_deleted = True
            entidadeUser.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
             return Response("entidade.errors", status=status.HTTP_400_BAD_REQUEST)



    @action(
        detail=True,
        methods=['GET'],
    )
    def getFornecedors(self, request, *args, **kwargs):
        transformer = self.get_object()
        fornecedores = Fornecedor.objects.filter(entidade=transformer)
        fornecedores =FornecedorSerializer(fornecedores, many=True)
        return Response(fornecedores.data, status.HTTP_200_OK)


    @action(
        detail=True,
        methods=['POST'],
    )
    def logoPost(self, request, *args, **kwargs):

        transformer = self.get_object()
        entidade = Entidade.objects.get(id=transformer.id)
       
        request.data['entidade'] = str(entidade.id)
        uploaded_file = request.FILES['ficheiro']

        if DiscManegar.freeSpace(entidade.id, request.FILES['ficheiro']):
            resposta = {'alert_error': 'Nao e possivel fazer upload de ficheiro<br><b>Contacte o adminstrador</b>'}
            return Response(resposta , status=status.HTTP_400_BAD_REQUEST)
        


        try:
            fcr = Ficheiros.objects.get(entidade=entidade, funcionalidade='Logo')
            fcr.delete()
            DiscManegar.recoverSpace(entidade.id, fcr)
        except:
            print('Nao apgaou')
    

        request.data['size'] = uploaded_file.size
        request.data['modelo'] = 'Entidade'
        request.data['estado'] = 'Activo'
        request.data['funcionalidade'] = 'Logo'

        ficheiro = FicheiroGravarSerializer(data=request.data)
        if ficheiro.is_valid(raise_exception=True):
            ficheiro.save()
            ficheiro = FicheiroSerializer(Ficheiros.objects.get(id=ficheiro.data['id']))
            DiscManegar.updateSpace(entidade.id, request.FILES['ficheiro'])
            return Response(ficheiro.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ficheiro.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(
        detail=True,
        methods=['GET'],
    )
    def qr(self, request, pk):
        id = pk
        var_qr = {}
        origin = request.headers['Origin']
        LANGUAGE_CODE = 'pt-pt'

        TIME_ZONE = 'UTC'
        settings.LANGUAGE_CODE = 'pt-pt'
        # django.setup()
        print(settings.LANGUAGE_CODE)

        root = settings.MEDIA_ROOT
        lingua = self.request.query_params.get('lang')

        ean = barcode.get('code128', id, writer=ImageWriter())
        filename = ean.save(str(root) +'/' + str(random.random()) + 'qr' + str(random.random()))

        file = Image.open(str(filename))
        file = open(str(filename), 'rb').read()


        blob_barcode = base64.b64encode((file))
        if os.path.exists(filename):
            os.remove(filename)


        qr = qrcode.QRCode(box_size=2)
        qr.add_data(str('var_qr'))
        qr.make()
        img_qr = qr.make_image()
        # img_qr.
        img = img_qr.get_image()

        name = str(root) +'/' + str(random.random()) + 'qr' + str(random.random()) + '.png'
        img_qr.save(name)
        file = Image.open(str(name))
        file = open(str(name), 'rb').read()
        blob = base64.b64encode(bytes(file))
        if os.path.exists(name):
            os.remove(name)


        template_path = 'core/entidade/qr_pdf.html'

        entidade = Entidade.objects.get(id=id)
 
        entidade = EntidadeSerializer(entidade)

        ficheiro  = Ficheiros.objects.get(entidade = id, funcionalidade = 'Logo')

        logo_name = ficheiro.ficheiro.path
        try:
            file = open(logo_name, 'rb').read()
            logo = base64.b64encode(file)
        except:
            logo = ''

        
        url = origin + '/#/?e=' + entidade.data['id'] + '&q=1' 
        var_qr['entidade'] = entidade.data['nome']
        for key, value in var_qr.items():
            url = url + '&' + key + '=' + value
        qr = qrcode.QRCode(box_size=2)
        qr.add_data(str(url))
        qr.make()
        img_qr = qr.make_image()
    

        name = str(root) +'/' + str(random.random()) + 'qr' + str(random.random()) + '.png'
        img_qr.save(name)
        file = Image.open(str(name))
        file = open(str(name), 'rb').read()
        qr_to_scan = base64.b64encode(bytes(file))
        if os.path.exists(name):
            os.remove(name)
        context = {
            'qr': blob,
            'qr_to_scan': qr_to_scan,
            'barcode': blob_barcode, 
            'entidade': entidade.data,
            'logo':logo,
            'titulo': Translate.st(lingua, 'QR'),
            'nome': Translate.st(lingua, 'Entidade'),
            'de': Translate.st(lingua, 'de'),
            'morada': Translate.st(lingua, 'Morada'),
            'pagina': Translate.st(lingua, 'Pagina')
        }
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        # if you need to download
        # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        response['Content-Disposition'] = 'filename="report.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf                  link_callback=link_callback
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response


    @action(
        detail=True,
        methods=['PUT'],
    )
    def perfilPut(self, request, pk):
        group = Group.objects.get(id=request.data['id'])
        group.name = request.data['name']
        group.save()
        
        perfil = {'id': group.id, 'name': group.name, 'alert_success': 'Perfil <b>'+ group.name + ' </b> actualizado com sucesso'}
        return Response(perfil, status.HTTP_201_CREATED)


    @action(
        detail=True,
        methods=['POST'],
    )
    def perfilPost(self, request, pk):      
        group = Group.objects.create(name=request.data['name'])
        entidade = Entidade.objects.get(id=pk)
        entidade.groups.add(group)

        perfil = {'id': group.id, 'name': group.name, 'alert_success': 'Perfil <b>'+ group.name + ' </b> criado com sucesso'}
        return Response(perfil, status.HTTP_201_CREATED)




class  SucursalAPIView(viewsets.ModelViewSet):
    #permission_classes = (permissions.IsAuthenticated)
    search_fields = ['id','nome']
    filter_backends = (filters.SearchFilter,)
    
    serializer_class = SucursalSerializer
    queryset = Sucursal.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter().order_by('-id')

    @action(
        detail=True,
        methods=['GET'],
    )
    def grupos(self, request, id):
        sucursalUserGroups = SucursalUserGroup.objects.all().filter(sucursal__id=id, user__id=request.user.id)
        suc = []
        for sucursalUserGroup in sucursalUserGroups:
            suc.append({'id': sucursalUserGroup.group.id, 'name': sucursalUserGroup.group.name})

        return Response(suc)

    @action(
        detail=True,
        methods=['GET'],
    )
    def Url(self, request, id):
        sucursal = Sucursal.objects.get(id=id)
        entidade = Entidade.objects.get(id=sucursal.entidade.id)
        return Response(str(entidade.tipo_entidade.id)+'/'+str(sucursal.entidade.id)+'/'+str(sucursal.id))
    
    

    @action(
        detail=True,
        methods=['GET'],
    )
    def getCapasSite(self, request, id):
        ficheiros = Ficheiros.objects.filter(sucursal__id=id, funcionalidade='CapaSite')
        ficheiros = FicheiroSerializer(ficheiros, many=True)
        data = (ficheiros.data)
        return Response(data, status=status.HTTP_200_OK)
    

    @action(
        detail=True,
        methods=['POST'],
    )
    def postCapasSite(self, request, id):
        sucursal = Sucursal.objects.get(id=id)

        request.data['entidade'] = str(sucursal.entidade.id)
        request.data['sucursal'] = str(sucursal.id)
        uploaded_file = request.FILES['ficheiro']

        if DiscManegar.freeSpace(sucursal.entidade.id, request.FILES['ficheiro']):
            resposta = {'alert_error': 'Nao e possivel fazer upload de ficheiro<br><b>Contacte o adminstrador</b>'}
            return Response(resposta , status=status.HTTP_400_BAD_REQUEST)

        request.data['size'] = uploaded_file.size
        request.data['modelo'] = 'sucursal'
        request.data['estado'] = 'Activo'
        request.data['funcionalidade'] = 'CapaSite'

        ficheiro = FicheiroGravarSerializer(data=request.data)
        if ficheiro.is_valid(raise_exception=True):
            ficheiro.save()
            ficheiro = FicheiroSerializer(Ficheiros.objects.get(id=ficheiro.data['id']))
            DiscManegar.updateSpace(sucursal.entidade.id, request.FILES['ficheiro'])
            return Response(ficheiro.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ficheiro.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(
        detail=True,
        methods=['GET'],
    )
    def getStocks(self, request, *args, **kwargs):
        transformer = self.get_object()
        stock = Stock.objects.filter(sucursal=transformer)
        stocks =StockSerializer(stock, many=True)
        return Response(stocks.data, status.HTTP_200_OK)
   

    

    @action(
        detail=True,
        methods=['GET'],
    )
    def qr(self, request, id):
        var_qr = {}
        origin = request.headers['Origin']
        LANGUAGE_CODE = 'pt-pt'

        TIME_ZONE = 'UTC'
        settings.LANGUAGE_CODE = 'pt-pt'
        # django.setup()
        print(settings.LANGUAGE_CODE)

        root = settings.MEDIA_ROOT
        lingua = self.request.query_params.get('lang')

        ean = barcode.get('code128', id, writer=ImageWriter())
        filename = ean.save(str(root) +'/' + str(random.random()) + 'qr' + str(random.random()))

        file = Image.open(str(filename))
        file = open(str(filename), 'rb').read()


        blob_barcode = base64.b64encode((file))
        if os.path.exists(filename):
            os.remove(filename)


        qr = qrcode.QRCode(box_size=2)
        qr.add_data(str('var_qr'))
        qr.make()
        img_qr = qr.make_image()
        # img_qr.
        img = img_qr.get_image()

        name = str(root) +'/' + str(random.random()) + 'qr' + str(random.random()) + '.png'
        img_qr.save(name)
        file = Image.open(str(name))
        file = open(str(name), 'rb').read()
        blob = base64.b64encode(bytes(file))
        if os.path.exists(name):
            os.remove(name)

        pk = id


        template_path = 'core/sucursal/qr_pdf.html'

        sucursal = Sucursal.objects.get(id=pk)
        sucursal1 = sucursal

    

        entidade = EntidadeSerializer(sucursal.entidade)

        sucursal = SucursalSerializer(sucursal)
        ficheiro  = Ficheiros.objects.get(entidade = sucursal1.entidade.id, funcionalidade = 'Logo')
        logo_name = ficheiro.ficheiro.path
        try:
            file = open(logo_name, 'rb').read()
            logo = base64.b64encode(bytes(file))
        except Exception as e:
            logo = logo_name.split('.')[-1]
        print(logo, logo_name, ficheiro)
        
        url = origin + '/#/?s=' + sucursal.data['id'] + '&q=1' 
        var_qr['entidade'] = entidade.data['nome']
        var_qr['sucursal'] = sucursal.data['nome']
        for key, value in var_qr.items():
            url = url + '&' + key + '=' + value
        # print(url)
        qr = qrcode.QRCode(box_size=2)
        qr.add_data(str(url))
        qr.make()
        img_qr = qr.make_image()
    

        name = str(root) +'/' + str(random.random()) + 'qr' + str(random.random()) + '.png'
        img_qr.save(name)
        file = Image.open(str(name))
        file = open(str(name), 'rb').read()
        qr_to_scan = base64.b64encode(bytes(file))


        if os.path.exists(name):
            os.remove(name)
        context = {
            'qr': blob,
            'qr_to_scan': qr_to_scan,
            'barcode': blob_barcode, 
            'entidade': entidade.data,
            'sucursal': sucursal.data,
            'logo':logo,
            'titulo': Translate.st(lingua, 'QR'),
            'nome': Translate.st(lingua, 'Sucursal'),
            'de': Translate.st(lingua, 'de'),
            'morada': Translate.st(lingua, 'Morada'),
            'pagina': Translate.st(lingua, 'Pagina')
        }
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        # if you need to download
        # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        response['Content-Disposition'] = 'filename="report.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        

        # create a pdf                  link_callback=link_callback
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return Response(context, status=status.HTTP_200_OK)
        return response

class  GrupoAPIView(viewsets.ModelViewSet):
    #permission_classes = (permissions.IsAuthenticated)
    # permission_classes = (permissions.IsAuthenticated, CoreAccessPermission)
    # permissions_rules = Permission.objects.filter(content_type__app_label='clinica',
    #                                               content_type__model='itempedidoexamemedico')
    paginator = None
    search_fields = ['id','name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = GrupoSerializer
    queryset = Group.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter().order_by('-codename')
        

    def retrieve(self, request, id, *args, **kwargs):
        try:
            request.query_params['permissions']
            grupo = Group.objects.get(id=id)
            permissions = grupo.permissions.annotate(content_type_model= F('content_type__model'), content_type_app= F('content_type__app_label'))
    
            per = []
            for permission in permissions:
                per.append({'id':permission.id, 'name':permission.name , 'codename':permission.codename, 'content_type':permission.content_type.id, 'content_type_model': permission.content_type_model, 'content_type_app': permission.content_type_app})
            print(per)
            return Response(per)
        except:
           pass

        try:

            transformer = self.get_object()
            grupo = GrupoSerializer(transformer)
            return Response(grupo.data, status=status.HTTP_200_OK)
        except Http404:
            pass
        return Response( status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request,id,  *args, **kwargs):
        g = Group.objects.get(id=id)
        g.name = request.data['name']
        g.save()
        add={'alert_success': '%-'+ request.data['name'] +'-% foi actualizado com sucesso'}
        data = json.loads(json.dumps({'id':g.id}))
        data.update(add)

        return Response(data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, id,  *args, **kwargs):
        g = Group.objects.get(id=id)
        nome = g.name
        g.delete()
        add={'alert_success': '<b>'+ nome +'</b> foi apagado com sucesso'}
        # return Response(add,status=status.HTTP_204_NO_CONTENT)
        return Response(add,status=status.HTTP_202_ACCEPTED)


    @action(
        detail=True,
        methods=['POST'],
    )
    def addPermission(self, request, id):
        grupo = Group.objects.get(id=id)

        content_type, created = ContentType.objects.get_or_create(
            model='uploadloaded',
        )
        custom_permission, created = Permission.objects.get_or_create(content_type= content_type, codename=request.data['codename'], defaults={'name': request.data['name']})
        grupo.permissions.add(custom_permission)
        permission = Permission.objects.get(id=custom_permission.id)

        per= {'id': permission.id, 'nome': permission.codename, 'nomeseparado':permission.name, 'alert_success': 'Permicao <b>' +permission.name + '</b> foi Adicionado consucesso'}
        return Response(per,status.HTTP_201_CREATED )

    


class  PermissionAPIView(viewsets.ModelViewSet):
 
    search_fields = ['id','name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = PermissionSerializer
    queryset = Permission.objects.annotate(content_type_model= F('content_type__model'), content_type_app= F('content_type__app_label'))
    lookup_field = "id"
    paginator = None


    def get_queryset(self):
        return self.queryset.filter().order_by('codename')

    def list(self, request, *args, **kwargs):
        self._paginator = None
        queryset = self.filter_queryset(self.get_queryset().filter().order_by('content_type__app_label', 'content_type__model', 'codename'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['POST'],
    )
    def addToGroup(self, request, id):
        grupo = Group.objects.get(id=request.data['id'])
        permission = Permission.objects.get(id=id)
        grupo.permissions.add(permission)
    
        per= {'id': permission.id, 'nome': permission.codename, 'nomeseparado':permission.name, 'alert_success': 'Permicao <b>' +permission.name + '</b> foi Adicionado consucesso'}
        return Response(per,status.HTTP_201_CREATED )


    @action(
        detail=True,
        methods=['POST'],
    )
    def removeFromGroup(self, request, id):
        # print(id, request.data) 
        grupo = Group.objects.get(id=request.data['id'])
        permission = Permission.objects.get(id=id)
        grupo.permissions.remove(permission)
    
        per= {'id': permission.id, 'nome': permission.codename, 'nomeseparado':permission.name, 'alert_info': 'Permicao <b>' +permission.name + '</b> foi removido consucesso'}
        return Response(per,status.HTTP_201_CREATED )


    @action(
        detail=True,
        methods=['POST'],
    )
    def addToUser(self, request, id):
        user = User.objects.get(id=request.data['user'])
        group = Group.objects.get(id=id)
        SucursalUserGroup.objects.create(sucursal_id=request.data['sucursal'], user=user, group=group)
        user.groups.add(group)
        per= {'alert_success': 'Perfil <b>' +group.name + '</b> foi Adicionado consucesso'}
        return Response(per,status.HTTP_201_CREATED )


    @action(
        detail=True,
        methods=['POST'],
    )
    def removeFromUser(self, request, id):
        user = User.objects.get(id=request.data['user'])
        group = Group.objects.get(id=id)
        SucursalUserGroup.objects.get(sucursal_id=request.data['sucursal'], user=user, group=group).delete()
        per= {'alert_success': 'Perfil <b>' +group.name + '</b> foi Removido consucesso'}
        return Response(per,status.HTTP_200_OK )


