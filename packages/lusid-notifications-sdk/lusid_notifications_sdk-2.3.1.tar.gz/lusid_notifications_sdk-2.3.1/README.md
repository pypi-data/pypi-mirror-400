<a id="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://fbn-prd.lusid.com/notification*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ApplicationMetadataApi* | [**list_access_controlled_resources**](docs/ApplicationMetadataApi.md#list_access_controlled_resources) | **GET** /api/metadata/access/resources | ListAccessControlledResources: Get resources available for access control
*DeliveriesApi* | [**list_deliveries**](docs/DeliveriesApi.md#list_deliveries) | **GET** /api/deliveries | ListDeliveries: List Deliveries
*EventTypesApi* | [**get_event_type**](docs/EventTypesApi.md#get_event_type) | **GET** /api/eventtypes/{eventType} | GetEventType: Gets the specified event type schema.
*EventTypesApi* | [**list_event_types**](docs/EventTypesApi.md#list_event_types) | **GET** /api/eventtypes | ListEventTypes: Lists all of the available event types.
*ManualEventApi* | [**trigger_manual_event**](docs/ManualEventApi.md#trigger_manual_event) | **POST** /api/manualevent | TriggerManualEvent: Trigger a manual event.
*NotificationsApi* | [**create_notification**](docs/NotificationsApi.md#create_notification) | **POST** /api/subscriptions/{scope}/{code}/notifications | CreateNotification: Add a Notification to a Subscription.
*NotificationsApi* | [**delete_notification**](docs/NotificationsApi.md#delete_notification) | **DELETE** /api/subscriptions/{scope}/{code}/notifications/{id} | DeleteNotification: Delete a notification for a given subscription.
*NotificationsApi* | [**get_notification**](docs/NotificationsApi.md#get_notification) | **GET** /api/subscriptions/{scope}/{code}/notifications/{id} | GetNotification: Get a notification on a subscription.
*NotificationsApi* | [**list_notifications**](docs/NotificationsApi.md#list_notifications) | **GET** /api/subscriptions/{scope}/{code}/notifications | ListNotifications: List all notifications on a subscription.
*NotificationsApi* | [**update_notification**](docs/NotificationsApi.md#update_notification) | **PUT** /api/subscriptions/{scope}/{code}/notifications/{id} | UpdateNotification: Update a Notification for a Subscription
*SubscriptionsApi* | [**create_subscription**](docs/SubscriptionsApi.md#create_subscription) | **POST** /api/subscriptions | CreateSubscription: Create a new subscription.
*SubscriptionsApi* | [**delete_subscription**](docs/SubscriptionsApi.md#delete_subscription) | **DELETE** /api/subscriptions/{scope}/{code} | DeleteSubscription: Delete a subscription.
*SubscriptionsApi* | [**get_subscription**](docs/SubscriptionsApi.md#get_subscription) | **GET** /api/subscriptions/{scope}/{code} | GetSubscription: Get a subscription.
*SubscriptionsApi* | [**list_subscriptions**](docs/SubscriptionsApi.md#list_subscriptions) | **GET** /api/subscriptions | ListSubscriptions: List subscriptions.
*SubscriptionsApi* | [**update_subscription**](docs/SubscriptionsApi.md#update_subscription) | **PUT** /api/subscriptions/{scope}/{code} | UpdateSubscription: Update an existing subscription.


<a id="documentation-for-models"></a>
## Documentation for Models

 - [AccessControlledAction](docs/AccessControlledAction.md)
 - [AccessControlledResource](docs/AccessControlledResource.md)
 - [ActionId](docs/ActionId.md)
 - [AmazonSqsNotificationType](docs/AmazonSqsNotificationType.md)
 - [AmazonSqsNotificationTypeResponse](docs/AmazonSqsNotificationTypeResponse.md)
 - [AmazonSqsPrincipalAuthNotificationType](docs/AmazonSqsPrincipalAuthNotificationType.md)
 - [AmazonSqsPrincipalAuthNotificationTypeResponse](docs/AmazonSqsPrincipalAuthNotificationTypeResponse.md)
 - [Attempt](docs/Attempt.md)
 - [AttemptStatus](docs/AttemptStatus.md)
 - [AzureServiceBusNotificationType](docs/AzureServiceBusNotificationType.md)
 - [AzureServiceBusTypeResponse](docs/AzureServiceBusTypeResponse.md)
 - [CreateNotificationRequest](docs/CreateNotificationRequest.md)
 - [CreateSubscription](docs/CreateSubscription.md)
 - [Delivery](docs/Delivery.md)
 - [EmailNotificationType](docs/EmailNotificationType.md)
 - [EmailNotificationTypeResponse](docs/EmailNotificationTypeResponse.md)
 - [EventFieldDefinition](docs/EventFieldDefinition.md)
 - [EventTypeSchema](docs/EventTypeSchema.md)
 - [IdSelectorDefinition](docs/IdSelectorDefinition.md)
 - [IdentifierPartSchema](docs/IdentifierPartSchema.md)
 - [Link](docs/Link.md)
 - [LusidProblemDetails](docs/LusidProblemDetails.md)
 - [LusidValidationProblemDetails](docs/LusidValidationProblemDetails.md)
 - [ManualEvent](docs/ManualEvent.md)
 - [ManualEventBody](docs/ManualEventBody.md)
 - [ManualEventHeader](docs/ManualEventHeader.md)
 - [ManualEventRequest](docs/ManualEventRequest.md)
 - [MatchingPattern](docs/MatchingPattern.md)
 - [Notification](docs/Notification.md)
 - [NotificationStatus](docs/NotificationStatus.md)
 - [NotificationType](docs/NotificationType.md)
 - [NotificationTypeResponse](docs/NotificationTypeResponse.md)
 - [ResourceId](docs/ResourceId.md)
 - [ResourceListOfAccessControlledResource](docs/ResourceListOfAccessControlledResource.md)
 - [ResourceListOfDelivery](docs/ResourceListOfDelivery.md)
 - [ResourceListOfEventTypeSchema](docs/ResourceListOfEventTypeSchema.md)
 - [ResourceListOfNotification](docs/ResourceListOfNotification.md)
 - [ResourceListOfSubscription](docs/ResourceListOfSubscription.md)
 - [SmsNotificationType](docs/SmsNotificationType.md)
 - [SmsNotificationTypeResponse](docs/SmsNotificationTypeResponse.md)
 - [Subscription](docs/Subscription.md)
 - [UpdateNotificationRequest](docs/UpdateNotificationRequest.md)
 - [UpdateSubscription](docs/UpdateSubscription.md)
 - [WebhookNotificationType](docs/WebhookNotificationType.md)
 - [WebhookNotificationTypeResponse](docs/WebhookNotificationTypeResponse.md)

