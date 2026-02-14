from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Box, BoxImage, Location, Category
from .forms import BoxForm
from django.db.models import Q
from django.core.paginator import Paginator

# Imports für Feature Release 1.6.0
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q


@login_required
def dashboard(request):
    # 1. Suchbegriff aus der URL holen (z.B. ?q=Weihnachten)
    query = request.GET.get('q')
    
    # 2. Basis: Erstmal alle Boxen nehmen
    boxes = Box.objects.all().order_by('-updated_at')
    
    # 3. Wenn gesucht wurde, filtern wir die Liste
    if query:
        # Anpassung 1.5.3 Start
        # Wir bereinigen den Suchbegriff, indem wir eventuelle Punkte entfernen.
        # So funktioniert die Suche nach z.B. '94.123' und '94123' gleichermaßen.
        clean_query_for_label = query.replace('.', '')
        # Anpassung 1.5.3 Ende 

        boxes = boxes.filter(
                    Q(label__icontains=clean_query_for_label) | # Suche im Barcode 1.5.3 Anpassung alt: Q(label__icontains=query) |
            Q(description__icontains=query) |        # Suche in Beschreibung
            Q(location__name__icontains=query) |     # Suche im Lagerort-Namen
            Q(categories__name__icontains=query)     # Suche in Kategorien
        ).distinct() # distinct verhindert Duplikate, falls mehrere Kategorien treffen

    return render(request, 'inventory/dashboard.html', {
        'boxes': boxes,
        'total_count': boxes.count(), # Zählt jetzt nur die gefundenen Boxen
        'search_query': query         # Damit das Suchfeld gefüllt bleibt
    })

@login_required
def global_history(request):
    # Basis-Query: nur "sinnvolle" Einträge:
    # - mit Benutzer ODER
    # - mit Change-Reason ODER
    # - Erzeugt / Gelöscht (+ / -)
    history_qs = (
        Box.history.all()
        .select_related('history_user', 'location')
        .filter(
            Q(history_user__isnull=False) |
            Q(history_change_reason__isnull=False) |
            Q(history_type__in=['+', '-'])
        )
    )

    view_title = "Alle Aktivitäten"

    # Filter: nur eigene Aktivitäten
    user_filter = request.GET.get('user')
    if user_filter == 'me' and request.user.is_authenticated:
        history_qs = history_qs.filter(history_user=request.user)
        view_title = "Meine Aktivitäten"

    # Sortierung
    sort_key = request.GET.get('sort', 'wann')
    sort_dir = request.GET.get('dir', 'desc')

    valid_sort_fields = {
        'wann': 'history_date',
        'wer': 'history_user__username',
        'aktion': 'history_type',
        'box': 'label',
        'lagerort': 'location__name',
        'status': 'status',
    }

    db_field = valid_sort_fields.get(sort_key, 'history_date')

    if sort_dir == 'desc':
        order_by = f'-{db_field}'
    else:
        order_by = db_field

    history_qs = history_qs.order_by(order_by, '-history_id')

    # Pagination
    paginator = Paginator(history_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_params = request.GET.copy()
    current_params.pop('page', None)

    next_sort_dir = 'asc' if sort_dir == 'desc' else 'desc'

    return render(
        request,
        'inventory/global_history.html',
        {
            'page_obj': page_obj,
            'view_title': view_title,
            'current_sort': sort_key,
            'current_dir': sort_dir,
            'next_sort_dir': next_sort_dir,
            'query_params': current_params.urlencode(),
        },
    )

# View für die Changelog-Seite
@login_required
def changelog_view(request):
    return render(request, 'inventory/changelog.html')


# --- Feature Release 1.6.0: Stammdaten-Verwaltung (CRUD) ---
# Wir verwenden Class-Based Views (CBVs) für Standard-Operationen.
# Das LoginRequiredMixin stellt sicher, dass nur eingeloggte Benutzer zugreifen können.

# --- LAGERORT (LOCATION) VIEWS ---

class LocationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_location'
    model = Location
    template_name = 'inventory/location_list.html'          # Dieses Template müssen wir erstellen
    context_object_name = 'locations'                       # Name der Variable im Template
    ordering = ['name']                                     # Sortiert die Liste alphabetisch

class LocationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_location'
    model = Location
    fields = ['name', 'description', 'is_external']         # Welche Felder sollen im Formular sein?
    template_name = 'inventory/location_form.html'          # Dieses Template müssen wir erstellen
    success_url = reverse_lazy('location_list')             # Wohin nach erfolgreichem Speichern?

class LocationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_location'
    model = Location
    fields = ['name', 'description', 'is_external']
    template_name = 'inventory/location_form.html'          # Nutzt das gleiche Template wie CreateView
    success_url = reverse_lazy('location_list')

class LocationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_location'
    model = Location
    template_name = 'inventory/location_confirm_delete.html' # Dieses Template müssen wir erstellen
    success_url = reverse_lazy('location_list')

# --- Feature Release 1.6.0: KATEGORIEN (CATEGORY) VIEWS ---

class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_category'
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_category'
    model = Category
    fields = ['name', 'color'] # ACHTUNG: Felder an das Category-Model anpassen!
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_category'
    model = Category
    fields = ['name', 'color'] # ACHTUNG: Felder an das Category-Model anpassen!
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_category'
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    # --- Feature Release 1.6.0: BOX (BOX) VIEWS ---

class BoxListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_box'
    model = Box
    template_name = 'inventory/dashboard.html'              # Das Dashboard dient als Liste
    context_object_name = 'boxes'
    ordering = ['-updated_at']                              # Letzte Änderung zuerst
    raise_exception = False                                  # Zeigt 403 Fehler bei fehlender Berechtigung

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Parameter aus der URL holen
        search_query = self.request.GET.get('q')            # Suchbegriff aus dem Suchformular
        location_id = self.request.GET.get('location')      # Filter für Lagerort (Antippen)
        category_id = self.request.GET.get('category')      # Filter für Kategorie (Antippen)
        status_filter = self.request.GET.get('status')      # Filter für Status (Antippen der Badges)

        # --- LOGIK: GEZIELTE FILTER (Antippen von Badges/Links) ---
        if location_id:
            queryset = queryset.filter(location_id=location_id)
            
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # --- LOGIK: VOLLTEXTSUCHE (Manuelle Eingabe im Suchfeld) ---
        if search_query:
            # Mapping deutscher Begriffe auf die Datenbank-Werte (STATUS_CHOICES)
            status_map = {
                'gelagert': 'STORED',
                'verliehen': 'LENT',
                'zugriff': 'ACCESS',
                'extern': 'EXT',
                'transit': 'TRANSIT',
                'verloren': 'LOST',
                'unbekannt': 'LOST'
            }
            mapped_status = status_map.get(search_query.lower())

            # Suche über alle relevanten Felder mit Q-Objekten
            q_objects = Q(label__icontains=search_query) | \
                        Q(description__icontains=search_query) | \
                        Q(location__name__icontains=search_query) | \
                        Q(categories__name__icontains=search_query)

            # Falls der Suchbegriff einem Status entspricht, diesen in die Suche einbeziehen
            if mapped_status:
                q_objects |= Q(status=mapped_status)

            queryset = queryset.filter(q_objects).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # total_count muss auf dem bereits gefilterten Queryset basieren
        context['total_count'] = self.get_queryset().count()
        # Suchbegriff für das Template bereitstellen
        context['search_query'] = self.request.GET.get('q', '')
        return context
    

class BoxDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'inventory.view_box'
    model = Box
    template_name = 'inventory/box_detail.html'
    context_object_name = 'box'
    slug_field = 'label'
    slug_url_kwarg = 'label_id'

    def get_context_data(self, **kwargs):
        # 1. Rufe die Basis-Implementierung auf, um den Standard-Kontext zu erhalten
        context = super().get_context_data(**kwargs)

        # 2. Hole das aktuelle Box-Objekt und die zugehörigen Modelle
        box = self.get_object()
        Location = self.model._meta.get_field('location').related_model
        Category = self.model._meta.get_field('categories').related_model

        # 3. Hole die komplette Historie für diese Box, neueste zuerst
        #    Liste erzwingen, damit Index-Zugriffe und len() effizient sind
        history_records = list(
            box.history.all()
            .select_related('history_user')
            .order_by('-history_date', '-history_id')
        )

        # 4. Bereite die Daten so auf, wie das Template sie erwartet (mit Änderungsdetails)
        processed_history = []

        for i, record in enumerate(history_records):

            # 4a. Einträge mit Text (history_change_reason) immer direkt übernehmen.
            #     Das betrifft u. a.:
            #     - "Bild hinzugefügt: ..."
            #     - "Bild gelöscht: ..."
            #     - "Kategorien hinzugefügt/entfernt: ..."
            #     - "Status geändert: ..."
            if record.history_change_reason:
                processed_history.append({
                    'record': record,
                    'changes': [],  # Template zeigt dann nur den Text an
                })
                continue  # Für diese Einträge keine Feld-Diffs berechnen

            changes_list = []

            # Nur bei Änderungs-Einträgen (~) Diffs berechnen
            if record.history_type == '~' and i + 1 < len(history_records):
                prev_record = history_records[i + 1]

                try:
                    delta = record.diff_against(prev_record)
                except Exception:
                    delta = None

                if delta:
                    for change in delta.changes:
                        field_name = change.field

                        # Feldnamen lesbar machen, wenn möglich
                        try:
                            field_verbose_name = self.model._meta.get_field(field_name).verbose_name
                        except Exception:
                            field_verbose_name = field_name

                        old_value = change.old
                        new_value = change.new

                        # --- START: Logik zur "Übersetzung" der Werte in Klarnamen ---
                        if field_name == 'location':
                            old_obj = Location.objects.filter(pk=old_value).first()
                            new_obj = Location.objects.filter(pk=new_value).first()
                            old_value = old_obj.name if old_obj else "---"
                            new_value = new_obj.name if new_obj else "---"

                        elif field_name == 'status':
                            choices = dict(self.model.STATUS_CHOICES)
                            old_value = choices.get(old_value, old_value)
                            new_value = choices.get(new_value, new_value)

                        elif field_name == 'categories':
                            # Listen mit Dicts -> nur die IDs extrahieren
                            old_ids = [item['category'] for item in (old_value or [])]
                            new_ids = [item['category'] for item in (new_value or [])]

                            old_items = Category.objects.filter(pk__in=old_ids).values_list('name', flat=True)
                            new_items = Category.objects.filter(pk__in=new_ids).values_list('name', flat=True)

                            old_value = ", ".join(sorted(old_items)) or "Keine"
                            new_value = ", ".join(sorted(new_items)) or "Keine"

                        else:  # Fallback für andere Felder wie 'description'
                            old_value = old_value if old_value else "---"
                            new_value = new_value if new_value else "---"
                        # --- ENDE: Logik zur "Übersetzung" ---

                        changes_list.append(
                            {
                                'field': field_verbose_name,
                                'old': old_value,
                                'new': new_value,
                            }
                        )

            # 5. Anzeige-Logik:
            #    - Erstellen/Löschen immer
            #    - Änderungen nur, wenn es tatsächlich Feld-Änderungen gibt
            has_diffs = len(changes_list) > 0
            is_creation = record.history_type == '+'
            is_deletion = record.history_type == '-'

            include = (
                is_creation or
                is_deletion or
                has_diffs
            )

            if include:
                processed_history.append(
                    {
                        'record': record,
                        'changes': changes_list,
                    }
                )

        # 6. Füge die aufbereiteten Verlaufsdaten zum Kontext hinzu
        context['history_data'] = processed_history
        
        # 7. Gib den vollständigen Kontext zurück
        return context

class BoxCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_box'
    model = Box
    form_class = BoxForm
    template_name = 'inventory/box_form.html'

    def form_valid(self, form):
        # WICHTIG: User an die Box kleben, bevor gespeichert wird
        form.instance._history_user = self.request.user
        # Erst Box speichern
        response = super().form_valid(form)

        # Sicherstellen, dass auch das gespeicherte Objekt den User trägt,
        # bevor wir Bilder anlegen (für die Bild-Logs)
        self.object._history_user = self.request.user

        # Dann hochgeladene Bilder anlegen
        uploaded_files = self.request.FILES.getlist('image_upload')
        for file in uploaded_files:
            BoxImage.objects.create(box=self.object, image=file)

        return response

    def get_success_url(self):
        # Nach dem Anlegen zur Detailansicht der neuen Box
        return reverse_lazy('box_detail', kwargs={'label_id': self.object.label})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['box_detail'] = "Neue Box anlegen"
        return context    

class BoxImageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.change_box'
    model = BoxImage
    template_name = 'inventory/image_confirm_delete.html'
    context_object_name = 'image'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # User an die verknüpfte Box hängen, damit das Signal ihn sieht
        self.object.box._history_user = request.user
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        # Nach dem Löschen zurück zur Bearbeitungsseite der zugehörigen Box
        return reverse_lazy('box_edit', kwargs={'label_id': self.object.box.label})

class BoxUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_box'
    model = Box
    form_class = BoxForm 
    template_name = 'inventory/box_form.html'
    success_url = reverse_lazy('dashboard')
    slug_field = 'label' 
    slug_url_kwarg = 'label_id'

    def form_valid(self, form):
        # User an die Box hängen
        form.instance._history_user = self.request.user
        # Zuerst die Standard-Aktion ausführen (Box-Objekt speichern)
        response = super().form_valid(form)

        # User auch am gespeicherten Objekt setzen (für Bild-Logs)
        self.object._history_user = self.request.user

        # Jetzt die hochgeladenen Bilder verarbeiten
        uploaded_files = self.request.FILES.getlist('image_upload')
        for file in uploaded_files:
            BoxImage.objects.create(box=self.object, image=file)

        return response

    def get_success_url(self):
        # Nach dem Speichern zur Detailseite der gerade bearbeiteten Box weiterleiten
        return reverse_lazy('box_detail', kwargs={'label_id': self.object.label})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['box_detail'] = "Box bearbeiten"
        return context

class BoxDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_box'
    model = Box
    template_name = 'inventory/box_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    slug_field = 'label' 
    slug_url_kwarg = 'label_id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # User an die Box hängen, bevor gelöscht wird
        self.object._history_user = request.user
        return super().delete(request, *args, **kwargs)