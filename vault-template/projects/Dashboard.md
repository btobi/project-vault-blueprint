---
type: "[[Overview]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Task Dashboard

Live views over every `#todo` in the vault (line tasks and project header lines alike). Steer from here; the daily brief in `daily/` is the dated snapshot.

## 🔴 Overdue

```tasks
not done
path does not include templates
due before today
sort by due
```

## ☀️ Today

```tasks
not done
path does not include templates
(due on today) OR (scheduled on today) OR (due before today)
sort by priority
sort by due
```

## 📆 This week

```tasks
not done
path does not include templates
due after today
due before in 8 days
sort by due
```

## ⏳ Waiting / blocked

```tasks
not done
path does not include templates
(tag includes #waiting) OR (tag includes #blocked)
sort by due
```

## 💤 Someday (no date)

```tasks
not done
path does not include templates
no due date
no scheduled date
no happens date
group by filename
```

## 🚀 Active projects

All projects with `status` ≠ `done`.

![[Project.base#Active]]
