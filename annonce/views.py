# -*- coding: UTF-8 -*-
import operator
import random
from calendar import month_name

from datetime import date, datetime
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.aggregates import Count
from django.db.models.functions.datetime import TruncMonth
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from localflavor.tn.tn_governorates import GOVERNORATE_CHOICES
from annonce.forms import UserForm, UserUpdateForm, CVForm, PostForm, SearchForm, ApplyOfferForm
from annonce.models import Offer, User, ApplyOffer
from metadata.models import TanitJobsCategory


def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('recent_post_list'))
    # Per Region -------------------------
    qs_posts_per_region = Offer.objects.values('lieu').annotate(count=Count('lieu'))
    posts_per_region = [['Region', 'Count']]
    tn_state = [state[0] for state in GOVERNORATE_CHOICES]
    for state in tn_state:
        count = 0
        for obj in qs_posts_per_region:
            if obj['lieu']:
                if state.replace(' ', '').lower() in obj['lieu'].replace(' ', '').lower():  # TODO
                    count += obj['count']
        posts_per_region.append([state.title(), count])
    # Per Sector -------------------------
    qs_posts_per_sector = Offer.objects.values('sector_activity__name').annotate(
        count=Count('sector_activity')).order_by('count')
    posts_per_sector = [['Region', 'Count']]
    sum_qs_posts_per_sector = sum([obj['count'] for obj in qs_posts_per_sector])
    # other_count = 0
    for obj in qs_posts_per_sector:
        if float(obj['count']) / float(sum_qs_posts_per_sector) > 0.02:
            posts_per_sector.append([str(obj['sector_activity__name']), obj['count']])
            # else:
            #     other_count += obj['count']
    # posts_per_sector.append(['Other less 2%', other_count])
    # Par date -------------------------
    qs_posts_per_date = Offer.objects.annotate(month=TruncMonth('created_at')
                                               ).values('month').annotate(count=Count('id')
                                                                          ).values('month', 'count')
    posts_per_date = [['Month', 'Count']]
    for obj in qs_posts_per_date:
        posts_per_date.append([month_name[obj['month'].month], obj['count']])
    # Par Sector Per Region -------------------------
    sectors = TanitJobsCategory.objects.all()
    posts_per_sector_per_region_sectors = []
    posts_per_sector_per_region_data = []
    for state in tn_state:
        data = {'state': state.title()}
        for sector in sectors:
            data[sector.name] = 0
            filters = {'sector_activity__name': sector.name, 'lieu__icontains': state}
            values = ('sector_activity__name', 'lieu')
            annotate = {'count': Count('sector_activity')}
            qs = Offer.objects.filter(**filters).values(*values).annotate(**annotate).order_by('count')
            for val in qs:
                data[sector.name] += val['count']
        posts_per_sector_per_region_data.append(data)

    for sector in sectors:
        total_per_sector = sum([obj[sector.name] for obj in posts_per_sector_per_region_data])
        if float(total_per_sector) / float(sum_qs_posts_per_sector) >= 0.03:
            posts_per_sector_per_region_sectors.append(sector)
        else:
            for obj in posts_per_sector_per_region_data:
                obj.pop(sector.name)

    objects = []
    posts_per_sector_per_region_sectors.remove(TanitJobsCategory.objects.get(name='Autres'))
    for obj in posts_per_sector_per_region_data:
        data = [obj['state']]
        for sector in posts_per_sector_per_region_sectors:
            data.append(obj[sector.name])
        objects.append(data)

    return render(request, 'index.html', {'posts_per_region': posts_per_region,
                                          'posts_per_sector': posts_per_sector,
                                          'posts_per_date': posts_per_date,
                                          'posts_per_sector_per_region_data': objects,
                                          'posts_per_sector_per_region_sectors': posts_per_sector_per_region_sectors})


def register(request, position):
    if request.user.is_authenticated():
        return redirect(reverse('recent_post_list'))
    if position == 'employer':
        initial = {'position': '0'}
    else:
        initial = {'position': '1'}
    form = UserForm(initial=initial)
    if request.POST:
        data = request.POST.copy()
        data.update(initial)
        form = UserForm(data=data)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            if new_user.is_employer:
                return redirect(reverse('recent_post_list'))
            return redirect(reverse('recent_cv_list'))
        print form.errors
    return render(request, 'registration/register.html', context={'form': form, 'position': position})


@login_required()
def profile(request):
    form = UserUpdateForm(instance=request.user)
    if request.POST:
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.user.is_employer:
                return redirect(reverse('recent_post_list'))
            return redirect(reverse('recent_cv_list'))
    fields = (form[field] for field in UserUpdateForm.Meta.fields)
    return render(request, 'profile/edit.html', context={'form': fields})


@login_required()
def add_cv(request):
    form = CVForm(instance=request.user)
    if request.POST:
        form = CVForm(request.POST, request.FILES, instance=request.user, initial={'user': request.user})
        if form.is_valid():
            form.save()
            return redirect(reverse('add_cv'))
    return render(request, 'profile/add_cv.html', context={'form': form})


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Offer
    form_class = PostForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        return super(PostCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Offer
    form_class = PostForm


@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Offer
    success_url = reverse_lazy('my_post_list')


@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Offer
    paginate_by = 25
    context_object_name = 'offers_list'

    def get_paginate_value(self):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        qs = super(PostListView, self).get_queryset()
        qs = qs.filter(created_by=self.request.user)
        return qs


@method_decorator(login_required, name='dispatch')
class RecentOffers(UserPassesTestMixin, ListView):
    model = Offer
    paginate_by = 25
    template_name = 'post/list.html'
    context_object_name = 'offers_list'
    login_url = 'recent_cv_list'
    redirect_field_name = None

    def test_func(self):
        return self.request.user.is_employer

    def get_paginate_value(self):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        qs = super(RecentOffers, self).get_queryset()
        today = date.today()
        qs = qs.filter(created_at__gt=datetime(today.year, today.month, 1))
        if self.request.user.category.name != 'Tous secteurs':
            qs = qs.filter(Q(sector_activity__name=self.request.user.category.name))
        search = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        region = self.request.GET.get('region', self.request.user.lieu)
        if region:
            qs = qs.filter(Q(lieu__icontains=region) | Q(state=region))
        if search:
            qs = qs.filter(Q(slug__icontains=search) | Q(sector_activity__name__icontains=search))
        if category:
            qs = qs.filter(Q(sector_activity__name=category))
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        filters = Q()
        categories = {}
        if self.request.user.category.name != 'Tous secteurs':
            filters = Q(sector_activity__name=self.request.user.category.name)
        qs = Offer.objects.filter(filters).order_by('-created_at')
        slice = random.random() * (qs.count() - 10)
        kwargs['recent_offers'] = qs[slice: slice + 6]
        if self.request.user.category.name == 'Tous secteurs':
            for category in TanitJobsCategory.objects.all():
                qs = Offer.objects.values('sector_activity__name').filter(sector_activity=category).order_by(
                    '-created_at')
                count = qs.count()
                if count:
                    categories[category.name] = count
            kwargs['categories'] = []
            for obj in sorted(categories.iteritems(), key=operator.itemgetter(1), reverse=True)[:6]:
                kwargs['categories'].append({'name': obj[0], 'count': obj[1]})
        return super(RecentOffers, self).get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class RecentCV(ListView):
    model = User
    paginate_by = 25
    template_name = 'cv/list.html'
    context_object_name = 'cv_list'
    login_url = 'recent_post_list'
    redirect_field_name = None

    def test_func(self):
        return self.request.user.is_job_seekers

    def get_paginate_value(self):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        qs = super(RecentCV, self).get_queryset()
        qs = qs.filter(is_employer=True)
        if self.request.user.category.name != 'Tous secteurs':
            qs = qs.filter(Q(category__name=self.request.user.category.name))
        search = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        region = self.request.GET.get('region', self.request.user.lieu)
        if region:
            qs = qs.filter(Q(lieu=region))
        if search:
            qs = qs.filter(Q(slug__icontains=search) | Q(category__name__icontains=search))
        if category:
            qs = qs.filter(Q(category__name=category))
        return qs

    def get_context_data(self, **kwargs):
        filters = Q()
        categories = {}
        if self.request.user.category.name != 'Tous secteurs':
            filters = Q(category__name=self.request.user.category.name)
        qs = User.objects.filter(filters)
        slice = random.random() * (qs.count() - 10)
        # kwargs['recent_cv'] = qs[slice: slice + 6]

        if self.request.user.category.name == 'Tous secteurs':
            for category in TanitJobsCategory.objects.all():
                qs = User.objects.values('category__name').filter(category=category)
                count = qs.count()
                if count:
                    categories[category.name] = count
            kwargs['categories'] = []
            for obj in sorted(categories.iteritems(), key=operator.itemgetter(1), reverse=True)[:6]:
                kwargs['categories'].append({'name': obj[0], 'count': obj[1]})
        return super(RecentCV, self).get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class ArchivedOffers(UserPassesTestMixin, ListView):
    model = Offer
    paginate_by = 25
    template_name = 'post/list.html'
    context_object_name = 'offers_list'
    login_url = 'profile'
    redirect_field_name = None

    def test_func(self):
        return self.request.user.is_employer

    def get_paginate_value(self):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        qs = super(ArchivedOffers, self).get_queryset()
        today = date.today()
        qs = qs.filter(created_at__lt=datetime(today.year, today.month, 1))
        if self.request.user.category.name != 'Tous secteurs':
            qs = qs.filter(Q(sector_activity__name=self.request.user.category.name))
        search = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        region = self.request.GET.get('region', self.request.user.lieu)
        if region:
            qs = qs.filter(Q(lieu__icontains=region) | Q(state=region))
        if search:
            qs = qs.filter(Q(slug__icontains=search) | Q(sector_activity__name__icontains=search))
        if category:
            qs = qs.filter(Q(sector_activity__name=category))
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        filters = Q()
        categories = {}
        if self.request.user.category.name != 'Tous secteurs':
            filters = Q(sector_activity__name=self.request.user.category.name)
        qs = Offer.objects.filter(filters).order_by('-created_at')
        slice = random.random() * (qs.count() - 10)
        kwargs['recent_offers'] = qs[slice: slice + 6]
        kwargs['archived'] = True
        if self.request.user.category.name == 'Tous secteurs':
            for category in TanitJobsCategory.objects.all():
                qs = Offer.objects.values('sector_activity__name').filter(sector_activity=category).order_by(
                    '-created_at')
                count = qs.count()
                if count:
                    categories[category.name] = count
            kwargs['categories'] = []
            for obj in sorted(categories.iteritems(), key=operator.itemgetter(1), reverse=True)[:6]:
                kwargs['categories'].append({'name': obj[0], 'count': obj[1]})
        return super(ArchivedOffers, self).get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class OfferDetails(DetailView):
    model = Offer
    template_name = 'post/details.html'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        filters = Q()
        categories = {}
        if self.request.user.category.name != 'Tous secteurs':
            filters = Q(sector_activity__name=self.request.user.category.name)
        qs = Offer.objects.filter(filters)
        slice = random.random() * (qs.count() - 10)
        kwargs['recent_offers'] = qs[slice: slice + 6]

        if self.request.user.category.name == 'Tous secteurs':
            for category in TanitJobsCategory.objects.all():
                qs = Offer.objects.values('sector_activity__name').filter(sector_activity=category)
                count = qs.count()
                if count:
                    categories[category.name] = count
            kwargs['categories'] = []
            for obj in sorted(categories.iteritems(), key=operator.itemgetter(1), reverse=True)[:6]:
                kwargs['categories'].append({'name': obj[0], 'count': obj[1]})
        return super(OfferDetails, self).get_context_data(**kwargs)


@login_required
def apply_offer(request, pk, slug):
    if request.POST:
        if request.user.cv:
            obj = ApplyOfferForm(data={'offer': pk, 'user': request.user.id})
            if obj.is_valid():
                obj.save()
                messages.success(request, "your application was successfully submitted")
            else:
                messages.error(request, 'you already submitted in this offer')
        else:
            messages.error(request, "Please add your CV")
    return redirect(reverse('post_details', args=[pk, slug]))
