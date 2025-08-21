from datetime import date, timedelta
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UserRegisterForm, ProfileUpdateForm, HabitForm
from .models import Habit, Completion



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Account "{user.username}" created successfully! Please log in.'
            )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile.html', {'p_form': p_form})


@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    today = date.today()

    def get_streak(habit):
        dates = list(
            habit.completions
                 .order_by('-date')
                 .values_list('date', flat=True)
        )
        streak = 0
        cur = today
        for d in dates:
            if d == cur:
                streak += 1
                cur = cur.fromordinal(cur.toordinal() - 1)
            else:
                break
        return streak

    total = habits.count()
    done_count = 0
    habits_data = []

    for h in habits:
        comp = Completion.objects.filter(habit=h, date=today).first()
        cnt = comp.count if comp else 0

        is_done = cnt >= h.daily_goal
        if is_done:
            done_count += 1

        habits_data.append({
            'obj': h,
            'count': cnt,
            'goal': h.daily_goal,
            'streak': get_streak(h),
            'done': is_done,
        })

    all_done = (total > 0 and done_count == total)

    return render(request, 'habit_list.html', {
        'habits_data': habits_data,
        'total': total,
        'done_count': done_count,
        'all_done': all_done,
    })


@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.user = request.user
            new.save()
            messages.success(request, f'Habit "{new.name}" added.')
            return redirect('habit-list')
    else:
        form = HabitForm()
    return render(request, 'habit_form.html', {
        'form': form,
        'title': 'Add Habit'
    })


@login_required
def habit_update(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Habit "{habit.name}" updated.')
            return redirect('habit-list')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'habit_form.html', {
        'form': form,
        'title': 'Edit Habit'
    })


@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, f'Habit "{habit.name}" deleted.')
        return redirect('habit-list')
    return render(request, 'habit_confirm_delete.html', {'habit': habit})


@login_required
def increment_completion(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()
    comp, _ = Completion.objects.get_or_create(habit=habit, date=today)
    comp.count += 1
    comp.save()
    return redirect('habit-list')


@login_required
def decrement_completion(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()
    try:
        comp = Completion.objects.get(habit=habit, date=today)
        if comp.count > 0:
            comp.count -= 1
            comp.save()
    except Completion.DoesNotExist:
        pass
    return redirect('habit-list')

@login_required
def statistics(request):
    today = date.today()

    labels = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    habits = Habit.objects.filter(user=request.user).order_by('created_at')

    per_habit = []
    totals = [0] * 7  

    for habit in habits:
        counts = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            comp = Completion.objects.filter(habit=habit, date=d).first()
            cnt = comp.count if comp else 0
            counts.append(cnt)

        totals = [t + c for t, c in zip(totals, counts)]

        per_habit.append({
            'id': habit.id,
            'name': habit.name,
            'counts': counts,
            'goal': habit.daily_goal,
            'total7': sum(counts),
        })

    totals_sum = sum(totals)

    stats = {
        'labels': labels,
        'per_habit': [{ 'name': h['name'], 'counts': h['counts'] } for h in per_habit],
        'totals': totals,
    }
    stats_json = json.dumps(stats)

    context = {
        'labels': labels,
        'per_habit': per_habit,
        'totals': totals,
        'totals_sum': totals_sum,
        'stats_json': stats_json,
    }
    return render(request, 'statistics.html', context)
