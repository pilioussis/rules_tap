-- Orgs
INSERT INTO org_org (id, name, created, type) VALUES
  (1, 'Acme Corp',     '2025-01-15 10:00:00', 'AC'),
  (2, 'Beta LLC',      '2025-02-10 14:30:00', 'PE'),
  (3, 'Gamma Partners','2025-03-05 09:20:00', 'IN');

-- Users
INSERT INTO org_user (id, email, first_name, last_name, is_admin, created, deactivated, role, password) VALUES
  (1, 'admin@acme.com',   'Alice',   'Admin',     TRUE,  '2025-01-15 10:05:00', NULL,                     'AD', 'sha256'),
  (2, 'bob@beta.com',     'Bob',     'Builder',   FALSE, '2025-02-10 14:35:00', NULL,                     'AU', 'sha256'),
  (3, 'charlie@gamma.io', 'Charlie', 'Chaplin',   FALSE, '2025-03-06 11:00:00', '2025-04-01 12:00:00',    'PB', 'sha256'),
  (4, 'dana@acme.com',    'Dana',    'Scully',    FALSE, '2025-01-16 08:00:00', NULL,                     'AU', 'sha256'),
  (5, 'john@john.com',          '',        '',    FALSE, '2025-04-20 16:45:00', NULL,                     'PB', 'sha256');

-- Workers
INSERT INTO org_worker (id, org_id, created, type, name, description) VALUES
  (1, 1, '2025-01-16 08:10:00', 'EM', 'Eve Adams',      'Senior engineer'),
  (2, 1, '2025-01-20 09:15:00', 'CO', 'Frank Miller',   'Contracted UX designer'),
  (3, 2, '2025-02-11 10:00:00', 'UA', 'Grace Hopper',   'Undercover agent liaison'),
  (4, 2, '2025-02-15 13:20:00', 'EM', 'Hank Pym',       'Lab technician'),
  (5, 3, '2025-03-07 15:30:00', 'CO', 'Ivy League',     'QA contractor'),
  (6, 1, '2025-04-01 11:45:00', 'UA', 'Jack Sparrow',   'Deep-cover ops');