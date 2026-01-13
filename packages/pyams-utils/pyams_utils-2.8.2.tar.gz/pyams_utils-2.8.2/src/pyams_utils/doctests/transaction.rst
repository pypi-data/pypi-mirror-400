==============================
PyAMS_utils transaction module
==============================

The *transaction* module can be used to integrate elements which are not transactional by
nature into a running transaction; for example, an Elasticsearch or Redis operation, or even
an operation on the filesystem, can be set as *transactional*: if this case, the matching action
will only by done if the current transaction is committed without error, in a two-phases
commit *tpc_finish* step, and ignored otherwise!

These features relies on the *transaction* package.

We will test this module by creating a small *transactional* file deletion: if the transaction
is aborted, the action should be cancelled!

Let's start by creating a transaction *client*:

    >>> import os
    >>> import transaction
    >>> from pyams_utils.transaction import transactional, TransactionClient

    >>> class FileTestClient(TransactionClient):
    ...     def __init__(self, filename, use_transaction=True,
    ...                  transaction_manager=transaction.manager):
    ...         super().__init__(use_transaction, transaction_manager)
    ...         self.filename = filename
    ...         self.fd = None
    ...
    ...     @transactional
    ...     def create(self, mode='w'):
    ...         self.fd = open(self.filename, mode)
    ...
    ...     def close(self):
    ...         if self.fd is not None:
    ...             self.fd.close()
    ...
    ...     @transactional
    ...     def delete(self):
    ...         self.close()
    ...         if os.path.isfile(self.filename):
    ...             os.remove(self.filename)

We can now try to test our client:

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()
    >>> temp_file = os.path.join(temp_dir, 'test.txt')
    >>> client = FileTestClient(temp_file)
    >>> client.create()
    >>> client.close()
    >>> transaction.commit()

    >>> os.path.isfile(temp_file)
    True

We can now try to remove the file, but abort the transaction:

    >>> client.delete()
    >>> transaction.abort()

    >>> os.path.isfile(temp_file)
    True

    >>> client.delete()
    >>> transaction.commit()

    >>> os.path.isfile(temp_file)
    False

Transactional behaviour can be disabled at any moment:

    >>> client.use_transaction = False
    >>> client.create()
    >>> client.close()
    >>> transaction.abort()

    >>> os.path.isfile(temp_file)
    True

    >>> client.delete()
    >>> transaction.abort()

    >>> os.path.isfile(temp_file)
    False

    >>> client.use_transaction = True

You can also call a transactional method for immediate execution:

    >>> client.create(immediate=True)
    >>> client.close()
    >>> transaction.abort()

    >>> os.path.isfile(temp_file)
    True

    >>> client.delete(immediate=True)
    >>> transaction.abort()

    >>> os.path.isfile(temp_file)
    False

Transaction client also handles savepoints:

    >>> client.create()
    >>> client.close()
    >>> sp = transaction.savepoint()
    >>> client.delete()
    >>> sp.rollback()
    >>> transaction.commit()

    >>> os.path.isfile(temp_file)
    True

    >>> client.delete()
    >>> transaction.commit()

    >>> os.path.isfile(temp_file)
    False

Of course, savepoints should be used with care when using non natively transactionnal clients!
