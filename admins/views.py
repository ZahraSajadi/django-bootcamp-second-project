from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)


class AdminHomeView(View): ...


class AdminRoomListView(ListView): ...


class AdminRoomDetailView(DetailView): ...


class AdminRoomCreateView(CreateView): ...


class AdminRoomUpdateView(UpdateView): ...


class AdminRoomDeleteView(DeleteView): ...


class AdminTeamListView(ListView): ...


class AdminTeamDetailView(DetailView): ...


class AdminTeamCreateView(CreateView): ...


class AdminTeamUpdateView(UpdateView): ...


class AdminTeamDeleteView(DeleteView): ...


class AdminReservationListView(ListView): ...


class AdminReservationDetailView(DetailView): ...


class AdminReservationDeleteView(DeleteView): ...


class AdminUserListView(ListView): ...


class AdminUserDetailView(DetailView): ...


class AdminUserUpdateView(UpdateView): ...
