from prettytable import PrettyTable


def prepare_datasets_table(dataset_response):
    datasets_table = PrettyTable()
    datasets_table.field_names = ['Dataset ID', 'Dataset Name', 'Encryption Type', 'Created At', 'Updated At', 'Status']
    for item in dataset_response:
        datasets_table.add_row([
            item.id,
            item.name,
            item.encryption_type,
            item.created_at,
            item.updated_at,
            item.status
        ])
    return datasets_table
